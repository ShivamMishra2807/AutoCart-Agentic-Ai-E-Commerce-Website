"""
Saathi's memory of a customer, plus the personal touches in its replies.
Only signed-in customers get memory. It is small, readable and deletable (see /api/support/memory).
"""

import re
import zlib

from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import UserMemory
from .views import get_user_from_token

CATEGORY_WORDS = {
    'Electronics': ('phone', 'laptop', 'mouse', 'headphone', 'earbud', 'tv', 'camera', 'charger', 'speaker'),
    'Fashion': ('shirt', 'dress', 'shoe', 'jeans', 'kurta', 'saree', 'jacket'),
    'Home & Kitchen': ('kitchen', 'bottle', 'flask', 'cooker', 'mixer', 'lamp'),
    'Beauty & Personal Care': ('cream', 'shampoo', 'moisturi', 'serum', 'face wash'),
    'Sports & Fitness': ('gym', 'yoga', 'dumbbell', 'cricket', 'running'),
    'Books & Stationery': ('book', 'novel', 'notebook', 'pen'),
    'Toys & Baby Care': ('toy', 'baby', 'diaper'),
}
LEADS = ('Here you go, {n}.', 'Sure, {n}.', 'Got it, {n}.', 'Happy to help, {n}.')


def first_name(user):
    return (getattr(user, 'name', '') or '').split()[0] if user else ''


def learn(user, message):
    """Update the customer's memory from one message. Stores only categories, a budget and a short search list."""
    if not user:
        return None
    mem, _ = UserMemory.objects.get_or_create(userEmail=user.email.lower())
    low = message.lower()
    for cat, words in CATEGORY_WORDS.items():
        if any(w in low for w in words) and cat not in mem.interests:
            mem.interests = ([cat] + mem.interests)[:5]
    m = re.search(r'(?:under|below|within|upto|up to|budget(?: of)?)\s*(?:rs\.?|₹)?\s*([\d,]{3,7})', low)
    if m:
        mem.budgetMax = int(m.group(1).replace(',', ''))
    if len(low) > 3 and not low.startswith(('talk to', 'track', 'return')):
        mem.recentSearches = ([message[:60]] + [s for s in mem.recentSearches if s != message[:60]])[:5]
    mem.chatCount += 1
    mem.save()
    return mem


def personalise(user, reply, seed):
    """Put the customer's first name into the reply, once, in a natural lead-in."""
    n = first_name(user)
    if not n or n.lower() in reply.lower()[:80]:
        return reply
    return f"{LEADS[zlib.crc32(seed.encode()) % len(LEADS)].format(n=n)} {reply}"


def memory_note(mem):
    """A short line the language model can use to tailor its answer."""
    if not mem:
        return ''
    bits = []
    if mem.interests:
        bits.append('interested in ' + ', '.join(mem.interests[:3]))
    if mem.budgetMax:
        bits.append(f'usual budget about ₹{mem.budgetMax}')
    return '; '.join(bits)


@api_view(['GET', 'DELETE'])
@permission_classes([AllowAny])
def assistant_memory_view(request):
    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    if request.method == 'DELETE':
        UserMemory.objects.filter(userEmail=user.email.lower()).delete()
        return Response({'forgotten': True})
    mem = UserMemory.objects.filter(userEmail=user.email.lower()).first()
    return Response({'name': first_name(user), 'interests': mem.interests if mem else [], 'budgetMax': mem.budgetMax if mem else None,
                     'recentSearches': mem.recentSearches if mem else [], 'chats': mem.chatCount if mem else 0})
