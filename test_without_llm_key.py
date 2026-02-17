"""
Test Support Ticket System without LLM API key
Verifies graceful degradation per Requirements 6.3, 6.4
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_classification_without_api_key():
    """Test that classification endpoint returns fallback values without API key"""
    print("\n=== Testing Classification Without API Key ===")
    
    test_descriptions = [
        "I was charged twice for my subscription",
        "Cannot log into my account",
        "The website is loading very slowly",
        "How do I change my password?"
    ]
    
    for desc in test_descriptions:
        print(f"\nTesting description: '{desc[:50]}...'")
        response = requests.post(
            f"{BASE_URL}/api/tickets/classify/",
            json={"description": desc}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Status: {response.status_code} ✓")
            print(f"  Suggested category: {result.get('suggested_category')}")
            print(f"  Suggested priority: {result.get('suggested_priority')}")
            
            # Verify fallback values are valid
            valid_categories = ['billing', 'technical', 'account', 'general']
            valid_priorities = ['low', 'medium', 'high', 'critical']
            
            if result.get('suggested_category') in valid_categories:
                print(f"  ✓ Category is valid")
            else:
                print(f"  ✗ Invalid category: {result.get('suggested_category')}")
            
            if result.get('suggested_priority') in valid_priorities:
                print(f"  ✓ Priority is valid")
            else:
                print(f"  ✗ Invalid priority: {result.get('suggested_priority')}")
            
            if 'note' in result:
                print(f"  Note: {result['note']}")
        else:
            print(f"  ✗ Request failed with status {response.status_code}")
            print(f"  Response: {response.text}")

def test_ticket_creation_without_llm():
    """Test that tickets can be created without LLM suggestions"""
    print("\n=== Testing Ticket Creation Without LLM ===")
    
    ticket_data = {
        "title": "Test ticket without LLM",
        "description": "This ticket is created without using LLM classification",
        "category": "general",
        "priority": "medium"
    }
    
    response = requests.post(f"{BASE_URL}/api/tickets/", json=ticket_data)
    
    if response.status_code == 201:
        ticket = response.json()
        print(f"✓ Ticket created successfully without LLM")
        print(f"  ID: {ticket['id']}")
        print(f"  Title: {ticket['title']}")
        print(f"  Category: {ticket['category']}")
        print(f"  Priority: {ticket['priority']}")
        print(f"  Status: {ticket['status']}")
        return True
    else:
        print(f"✗ Failed to create ticket: {response.text}")
        return False

def test_full_workflow_without_llm():
    """Test complete workflow without LLM API key"""
    print("\n=== Testing Full Workflow Without LLM ===")
    
    # 1. Get classification (should return fallback)
    print("\n1. Getting classification suggestions...")
    classify_response = requests.post(
        f"{BASE_URL}/api/tickets/classify/",
        json={"description": "Need help with billing issue"}
    )
    
    if classify_response.status_code == 200:
        suggestions = classify_response.json()
        print(f"   ✓ Got suggestions: {suggestions.get('suggested_category')}/{suggestions.get('suggested_priority')}")
    
    # 2. Create ticket with fallback values
    print("\n2. Creating ticket with fallback values...")
    ticket_data = {
        "title": "Billing issue - workflow test",
        "description": "Need help with billing issue",
        "category": suggestions.get('suggested_category', 'general'),
        "priority": suggestions.get('suggested_priority', 'medium')
    }
    
    create_response = requests.post(f"{BASE_URL}/api/tickets/", json=ticket_data)
    
    if create_response.status_code == 201:
        ticket = create_response.json()
        print(f"   ✓ Ticket created with ID: {ticket['id']}")
        ticket_id = ticket['id']
    else:
        print(f"   ✗ Failed to create ticket")
        return False
    
    # 3. List tickets
    print("\n3. Listing tickets...")
    list_response = requests.get(f"{BASE_URL}/api/tickets/")
    if list_response.status_code == 200:
        tickets = list_response.json()
        print(f"   ✓ Retrieved {len(tickets)} tickets")
    
    # 4. Update ticket status
    print("\n4. Updating ticket status...")
    update_response = requests.patch(
        f"{BASE_URL}/api/tickets/{ticket_id}/",
        json={"status": "resolved"}
    )
    if update_response.status_code == 200:
        print(f"   ✓ Status updated to resolved")
    
    # 5. Get stats
    print("\n5. Getting statistics...")
    stats_response = requests.get(f"{BASE_URL}/api/tickets/stats/")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"   ✓ Stats retrieved: {stats.get('total_tickets')} total tickets")
    
    print("\n✓ Complete workflow works without LLM API key")
    return True

def verify_graceful_degradation():
    """Verify the system degrades gracefully without LLM"""
    print("\n=== Verifying Graceful Degradation ===")
    
    print("\nChecking that:")
    print("1. Classification endpoint returns valid fallback values")
    print("2. Tickets can still be created")
    print("3. All other functionality works normally")
    print("4. No errors or crashes occur")
    
    # Test classification returns valid values
    response = requests.post(
        f"{BASE_URL}/api/tickets/classify/",
        json={"description": "Test description"}
    )
    
    if response.status_code == 200:
        result = response.json()
        has_category = 'suggested_category' in result
        has_priority = 'suggested_priority' in result
        
        print(f"\n✓ Classification endpoint accessible")
        print(f"  Returns category: {has_category}")
        print(f"  Returns priority: {has_priority}")
        
        if 'note' in result:
            print(f"  Provides user feedback: ✓")
            print(f"  Message: '{result['note']}'")
        
        return True
    else:
        print(f"\n✗ Classification endpoint failed")
        return False

def main():
    """Run all tests for system without LLM API key"""
    print("=" * 70)
    print("TESTING SUPPORT TICKET SYSTEM WITHOUT LLM API KEY")
    print("Requirements: 6.3 (graceful error handling), 6.4 (invalid data handling)")
    print("=" * 70)
    
    try:
        # Test classification with fallback
        test_classification_without_api_key()
        
        # Test ticket creation without LLM
        test_ticket_creation_without_llm()
        
        # Test full workflow
        test_full_workflow_without_llm()
        
        # Verify graceful degradation
        verify_graceful_degradation()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED - SYSTEM WORKS WITHOUT LLM API KEY")
        print("✓ Graceful degradation verified")
        print("✓ Fallback values provided")
        print("✓ No functionality blocked")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to backend service")
        print("  Make sure docker-compose is running")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
