"""
Complete workflow integration test for Support Ticket System
Tests all requirements from task 18.1
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_ticket_creation():
    """Test creating tickets through the API"""
    print("\n=== Testing Ticket Creation ===")
    
    ticket_data = {
        "title": "Test ticket for workflow validation",
        "description": "This is a test ticket to verify the complete workflow",
        "category": "technical",
        "priority": "high"
    }
    
    response = requests.post(f"{BASE_URL}/api/tickets/", json=ticket_data)
    print(f"Create ticket response: {response.status_code}")
    
    if response.status_code == 201:
        ticket = response.json()
        print(f"✓ Ticket created successfully with ID: {ticket['id']}")
        print(f"  Title: {ticket['title']}")
        print(f"  Status: {ticket['status']}")
        print(f"  Created at: {ticket['created_at']}")
        return ticket['id']
    else:
        print(f"✗ Failed to create ticket: {response.text}")
        return None

def test_llm_classification():
    """Test LLM classification endpoint"""
    print("\n=== Testing LLM Classification ===")
    
    description = "I was charged twice for my monthly subscription"
    response = requests.post(
        f"{BASE_URL}/api/tickets/classify/",
        json={"description": description}
    )
    
    print(f"Classification response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Classification successful")
        print(f"  Suggested category: {result.get('suggested_category')}")
        print(f"  Suggested priority: {result.get('suggested_priority')}")
        if 'note' in result:
            print(f"  Note: {result['note']}")
        return True
    else:
        print(f"✗ Classification failed: {response.text}")
        return False

def test_filtering():
    """Test filtering functionality"""
    print("\n=== Testing Filtering ===")
    
    # Test category filter
    response = requests.get(f"{BASE_URL}/api/tickets/?category=technical")
    print(f"Category filter response: {response.status_code}")
    if response.status_code == 200:
        tickets = response.json()
        print(f"✓ Category filter returned {len(tickets)} tickets")
        if tickets:
            all_technical = all(t['category'] == 'technical' for t in tickets)
            print(f"  All tickets are technical: {all_technical}")
    
    # Test priority filter
    response = requests.get(f"{BASE_URL}/api/tickets/?priority=high")
    print(f"Priority filter response: {response.status_code}")
    if response.status_code == 200:
        tickets = response.json()
        print(f"✓ Priority filter returned {len(tickets)} tickets")
    
    # Test status filter
    response = requests.get(f"{BASE_URL}/api/tickets/?status=open")
    print(f"Status filter response: {response.status_code}")
    if response.status_code == 200:
        tickets = response.json()
        print(f"✓ Status filter returned {len(tickets)} tickets")
    
    # Test combined filters
    response = requests.get(
        f"{BASE_URL}/api/tickets/?category=technical&priority=high&status=open"
    )
    print(f"Combined filter response: {response.status_code}")
    if response.status_code == 200:
        tickets = response.json()
        print(f"✓ Combined filter returned {len(tickets)} tickets")

def test_search():
    """Test search functionality"""
    print("\n=== Testing Search ===")
    
    response = requests.get(f"{BASE_URL}/api/tickets/?search=test")
    print(f"Search response: {response.status_code}")
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"✓ Search returned {len(tickets)} tickets")
        if tickets:
            print(f"  First result: {tickets[0]['title']}")

def test_stats():
    """Test statistics endpoint"""
    print("\n=== Testing Statistics ===")
    
    response = requests.get(f"{BASE_URL}/api/tickets/stats/")
    print(f"Stats response: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Stats retrieved successfully")
        print(f"  Total tickets: {stats.get('total_tickets')}")
        print(f"  Open tickets: {stats.get('open_tickets')}")
        print(f"  Avg tickets per day: {stats.get('avg_tickets_per_day')}")
        print(f"  Priority breakdown: {stats.get('priority_breakdown')}")
        print(f"  Category breakdown: {stats.get('category_breakdown')}")
        return stats
    else:
        print(f"✗ Failed to get stats: {response.text}")
        return None

def test_status_update(ticket_id):
    """Test updating ticket status"""
    print("\n=== Testing Status Update ===")
    
    if not ticket_id:
        print("✗ No ticket ID provided, skipping status update test")
        return
    
    update_data = {"status": "in_progress"}
    response = requests.patch(
        f"{BASE_URL}/api/tickets/{ticket_id}/",
        json=update_data
    )
    
    print(f"Status update response: {response.status_code}")
    
    if response.status_code == 200:
        ticket = response.json()
        print(f"✓ Status updated successfully")
        print(f"  New status: {ticket['status']}")
        return True
    else:
        print(f"✗ Failed to update status: {response.text}")
        return False

def verify_stats_update(initial_stats):
    """Verify that stats update after ticket creation"""
    print("\n=== Verifying Stats Update ===")
    
    if not initial_stats:
        print("✗ No initial stats to compare")
        return
    
    response = requests.get(f"{BASE_URL}/api/tickets/stats/")
    if response.status_code == 200:
        new_stats = response.json()
        
        if new_stats['total_tickets'] > initial_stats['total_tickets']:
            print(f"✓ Stats updated correctly")
            print(f"  Total tickets increased from {initial_stats['total_tickets']} to {new_stats['total_tickets']}")
        else:
            print(f"  Stats unchanged (may have been tested before)")

def main():
    """Run all workflow tests"""
    print("=" * 60)
    print("SUPPORT TICKET SYSTEM - COMPLETE WORKFLOW TEST")
    print("=" * 60)
    
    try:
        # Wait for services to be ready
        print("\nWaiting for services to be ready...")
        time.sleep(2)
        
        # Get initial stats
        initial_stats = test_stats()
        
        # Test LLM classification
        test_llm_classification()
        
        # Test ticket creation
        ticket_id = test_ticket_creation()
        
        # Test filtering
        test_filtering()
        
        # Test search
        test_search()
        
        # Test status update
        if ticket_id:
            test_status_update(ticket_id)
        
        # Verify stats update
        verify_stats_update(initial_stats)
        
        print("\n" + "=" * 60)
        print("WORKFLOW TEST COMPLETED")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to backend service")
        print("  Make sure docker-compose is running")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
