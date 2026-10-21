"""
Comprehensive Unit & Integration tests for AutoCart LangChain Integration.
Tests:
- Document Converters (Django Model to LangChain Document)
- LangChain Tools (@tool) with Pydantic Argument Schemas
- LangChain Expression Language (LCEL) Chains
- UnifiedLLMRunnable Adapter
- Authorization & Privacy Guards (Customer Order isolation, Admin audit privilege)
- Integration with Saathi (LangGraph + LangChain) and Munim (Seller Assistant)
"""

from django.test import TestCase
from api.langchain_module import (
    LangChainLLMRunnable,
    product_to_langchain_doc,
    policy_to_langchain_doc,
    get_saathi_lcel_chain,
    get_munim_lcel_chain,
    get_discovery_lcel_chain,
    get_customer_engagement_lcel_chain,
    get_admin_audit_lcel_chain,
    search_catalog_tool,
    get_product_details_tool,
    check_order_status_tool,
    get_marketplace_policy_tool,
    add_to_cart_tool,
    admin_audit_applications_tool,
    LANGCHAIN_TOOLS,
)
from api.models import Product, Order, SellerApplication
from api import agent_graph
from api.seller_assistant import smart_answer


class LangChainComprehensiveIntegrationTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            id='prod-lc-01',
            name='Mumbai Handloom Cotton Kurta',
            category='Fashion',
            brand='Khadi Emporium',
            price=899,
            rating=4.8,
            reviewCount=112,
            stock=15,
            seller='Khadi Emporium Mumbai',
            description='Authentic breathable cotton kurta made in Mumbai'
        )
        self.order = Order.objects.create(
            id='ORD-LC-2026',
            customerName='Pooja Desai',
            customerEmail='pooja.desai@example.com',
            customerPhone='9820098200',
            totalAmount=899,
            status='CONFIRMED',
            paymentStatus='PAID',
            items=[{'productId': 'prod-lc-01', 'name': 'Mumbai Handloom Cotton Kurta', 'price': 899, 'quantity': 1}]
        )
        self.seller_app = SellerApplication.objects.create(
            id='app-lc-test-01',
            companyName='Bombay Spices LLP',
            applicantName='Vikram Mehta',
            phone='9811122233',
            email='vikram@bombayspices.in',
            city='Mumbai',
            addressState='Maharashtra',
            pincode='400001',
            status='SUBMITTED',
            riskScore=15,
            riskCategory='Low'
        )

    def test_document_converters(self):
        """Test conversion of Django Product models and policies into LangChain Documents."""
        doc = product_to_langchain_doc(self.product)
        self.assertIn('Mumbai Handloom Cotton Kurta', doc.page_content)
        self.assertIn('Khadi Emporium', doc.page_content)
        self.assertEqual(doc.metadata['price'], 899.0)
        self.assertEqual(doc.metadata['kind'], 'product')
        self.assertEqual(doc.metadata['id'], 'prod-lc-01')

        policy_doc = policy_to_langchain_doc('returns', 'Delivered items can be returned within 7 days.')
        self.assertEqual(policy_doc.metadata['kind'], 'policy')
        self.assertEqual(policy_doc.metadata['topic'], 'returns')
        self.assertIn('7 days', policy_doc.page_content)

    def test_search_catalog_tool(self):
        """Test LangChain search_catalog_tool with query and price ceiling."""
        res = search_catalog_tool.invoke({'query': 'Kurta', 'max_price': 1000.0})
        self.assertIn('Mumbai Handloom Cotton Kurta', res)
        self.assertIn('Rs. 899', res)

        res_expensive = search_catalog_tool.invoke({'query': 'Kurta', 'max_price': 500.0})
        # 899 is over 500
        self.assertTrue('No matching products found' in res_expensive or 'Cotton Kurta' not in res_expensive)

    def test_get_product_details_tool(self):
        """Test LangChain get_product_details_tool retrieves verified product specs."""
        details = get_product_details_tool.invoke({'product_id': 'prod-lc-01'})
        self.assertIn('Mumbai Handloom Cotton Kurta', details)
        self.assertIn('15 units available', details)
        self.assertIn('Khadi Emporium', details)

        notFound = get_product_details_tool.invoke({'product_id': 'prod-fake-999'})
        self.assertIn('not found', notFound)

    def test_check_order_status_tool_with_privacy(self):
        """Test order status lookup with customer authorization verification."""
        # 1. Correct customer email
        res_ok = check_order_status_tool.invoke({
            'order_id': 'ORD-LC-2026',
            'customer_email': 'pooja.desai@example.com'
        })
        self.assertIn('CONFIRMED', res_ok)
        self.assertIn('899', res_ok)

        # 2. Cross-customer privacy violation attempt
        res_unauth = check_order_status_tool.invoke({
            'order_id': 'ORD-LC-2026',
            'customer_email': 'stranger@example.com'
        })
        self.assertIn('Unauthorized', res_unauth)

    def test_get_marketplace_policy_tool(self):
        """Test policy retrieval tool."""
        res_del = get_marketplace_policy_tool.invoke({'topic': 'delivery'})
        self.assertIn('Delivery:', res_del)

        res_ret = get_marketplace_policy_tool.invoke({'topic': 'returns'})
        self.assertIn('Returns:', res_ret)

    def test_add_to_cart_tool(self):
        """Test LangChain add_to_cart_tool performs stock validation and cart update."""
        res = add_to_cart_tool.invoke({'product_id': 'prod-lc-01', 'quantity': 2})
        self.assertIn('Success', res)
        self.assertIn('Mumbai Handloom Cotton Kurta', res)

        # Exceeding stock
        res_oversell = add_to_cart_tool.invoke({'product_id': 'prod-lc-01', 'quantity': 999})
        self.assertIn('Error', res_oversell)
        self.assertIn('stock', res_oversell.lower())

    def test_admin_audit_applications_tool_authorization(self):
        """Test admin audit tool strictly enforces admin/staff role check."""
        # 1. Ordinary customer / guest denied
        denied = admin_audit_applications_tool.invoke({'user_role': 'CUSTOMER'})
        self.assertIn('Access Denied', denied)

        # 2. Administrator permitted
        res_admin = admin_audit_applications_tool.invoke({'user_role': 'ADMIN'})
        self.assertIn('pending applications', res_admin.lower())

        # 3. Audit specific application ID
        res_single = admin_audit_applications_tool.invoke({
            'user_role': 'ADMIN',
            'application_id': 'app-lc-test-01'
        })
        self.assertIn('Bombay Spices', res_single)
        self.assertIn('Risk Score', res_single)

    def test_lcel_chains_construction(self):
        """Verify all LangChain LCEL pipelines construct properly with prompt, llm, and output parser."""
        saathi = get_saathi_lcel_chain()
        self.assertIsNotNone(saathi)

        munim = get_munim_lcel_chain()
        self.assertIsNotNone(munim)

        discovery = get_discovery_lcel_chain()
        self.assertIsNotNone(discovery)

        engagement = get_customer_engagement_lcel_chain()
        self.assertIsNotNone(engagement)

        admin_audit = get_admin_audit_lcel_chain()
        self.assertIsNotNone(admin_audit)

    def test_langchain_runnable_adapter(self):
        """Test LangChainLLMRunnable invokes cleanly without unhandled exceptions."""
        runnable = LangChainLLMRunnable(temperature=0.2, max_tokens=100)
        # Even with no external LLM configured, invoke returns a safe string (empty or fallback) without raising
        res = runnable.invoke("Test ping")
        self.assertIsInstance(res, str)

    def test_agent_graph_langchain_integration(self):
        """Test Saathi LangGraph pipeline seamlessly calls LCEL chain."""
        r = agent_graph.run('kurta under 1000')
        self.assertIn(r['intent'], ['search', 'catalog', 'faq', 'browse'])
        self.assertTrue(len(r.get('products', [])) > 0 or r.get('reply'))

    def test_seller_assistant_langchain_integration(self):
        """Test Munim seller assistant invokes LCEL chain."""
        res = smart_answer(company='Bombay Spices LLP', first='Vikram', message='How are my products doing?')
        self.assertIn('answer', res)
        self.assertIn('provider', res)
