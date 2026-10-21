import React from 'react';
import EnquiryInbox from '../../storefront/EnquiryInbox';

export default function Enquiries() {
  return (
    <div>
      <h1 className="text-2xl font-extrabold text-gray-900">Customer enquiries</h1>
      <p className="text-gray-600 text-sm mt-1">Questions from visitors and customers. Product questions go to the seller first, and you can answer any of them.</p>
      <EnquiryInbox title="Enquiries" />
    </div>
  );
}
