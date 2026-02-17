#!/usr/bin/env python
"""
Simple script to test API endpoints functionality.
This verifies that all endpoints are accessible and respond correctly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from tickets.models import Ticket
import json

def test_endpoints():
    """Test all API endpoints"""
    client = Client()
    print("Testing API Endpoints...")
    print("=" * 60)
    
    # Clean up any existing test data
    Ticket.objects.all().delete()
    
    # Test 1: Create a ticket (POST /api/tickets/)
    print("\n1. Testing POST /api/tickets/ (Create ticket)")
    response = client.post('/api/tickets/', {
        'title': 'Test ticket',
        'description': 'This is a test description',
        'category': 'technical',
        'priority': 'high'
    }, content_type='application/json')
    
    if response.status_code == 201:
        print(f"   ✓ Status: {response.status_code} (Created)")
        ticket_data = response.json()
        ticket_id = ticket_data['id']
        print(f"   ✓ Created ticket ID: {ticket_id}")
    else:
        print(f"   ✗ Status: {response.status_code}")
        print(f"   ✗ Response: {response.content}")
        return False
    
    # Test 2: List tickets (GET /api/tickets/)
    print("\n2. Testing GET /api/tickets/ (List tickets)")
    response = client.get('/api/tickets/')
    
    if response.status_code == 200:
        print(f"   ✓ Status: {response.status_code} (OK)")
        tickets = response.json()
        print(f"   ✓ Found {len(tickets)} ticket(s)")
    else:
        print(f"   ✗ Status: {response.status_code}")
        return False
    
    # Test 3: Filter tickets (GET /api/tickets/?category=technical)
    print("\n3. Testing GET /api/tickets/?category=technical (Filter)")
    response = client.get('/api/tickets/?category=technical')
    
    if response.status_code == 200:
        print(f"   ✓ Status: {response.status_code} (OK)")
        tickets = response.json()
        print(f"   ✓ Found {len(tickets)} technical ticket(s)")
    else:
        print(f"   ✗ Status: {response.status_code}")
        return False
    
    # Test 4: Search tickets (GET /api/tickets/?search=test)
    print("\n4. Testing GET /api/tickets/?search=test (Search)")
    response = client.get('/api/tickets/?search=test')
    
    if response.status_code == 200:
        print(f"   ✓ Status: {response.status_code} (OK)")
        tickets = response.json()
        print(f"   ✓ Found {len(tickets)} matching ticket(s)")
    else:
        print(f"   ✗ Status: {response.status_code}")
        return False
    
    # Test 5: Update ticket (PATCH /api/tickets/<id>/)
    print(f"\n5. Testing PATCH /api/tickets/{ticket_id}/ (Update ticket)")
    response = client.patch(f'/api/tickets/{ticket_id}/', {
        'status': 'in_progress'
    }, content_type='application/json')
    
    if response.status_code == 200:
        print(f"   ✓ Status: {response.status_code} (OK)")
        updated_ticket = response.json()
        print(f"   ✓ Updated status to: {updated_ticket['status']}")
    else:
        print(f"   ✗ Status: {response.status_code}")
        return False
    
    # Test 6: Get stats (GET /api/tickets/stats/)
    print("\n6. Testing GET /api/tickets/stats/ (Statistics)")
    response = client.get('/api/tickets/stats/')
    
    if response.status_code == 200:
        print(f"   ✓ Status: {response.status_code} (OK)")
        stats = response.json()
        print(f"   ✓ Total tickets: {stats['total_tickets']}")
        print(f"   ✓ Open tickets: {stats['open_tickets']}")
        print(f"   ✓ Avg per day: {stats['avg_tickets_per_day']}")
    else:
        print(f"   ✗ Status: {response.status_code}")
        return False
    
    # Test 7: Classify ticket (POST /api/tickets/classify/)
    print("\n7. Testing POST /api/tickets/classify/ (LLM Classification)")
    has_api_key = bool(os.environ.get('OPENAI_API_KEY'))
    print(f"   OPENAI_API_KEY is {'SET' if has_api_key else 'NOT SET'}")
    
    response = client.post('/api/tickets/classify/', {
        'description': 'I was charged twice for my subscription'
    }, content_type='application/json')
    
    if response.status_code == 200:
        print(f"   ✓ Status: {response.status_code} (OK)")
        classification = response.json()
        print(f"   ✓ Suggested category: {classification.get('suggested_category')}")
        print(f"   ✓ Suggested priority: {classification.get('suggested_priority')}")
        if 'note' in classification:
            print(f"   ℹ Note: {classification['note']}")
    else:
        print(f"   ✗ Status: {response.status_code}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All API endpoints are working correctly!")
    print("=" * 60)
    
    # Clean up
    Ticket.objects.all().delete()
    
    return True

if __name__ == '__main__':
    try:
        success = test_endpoints()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
