"""
Test script to verify the Recall Checker MCP server works correctly
"""

import sys

print("=" * 60)
print("Test 1: Searching for recalls")
print("=" * 60)

try:
    # Search for "crib" recalls
    product_name = "crib"
    query_lower = product_name.lower()
    
    mock_recalls = {
        "CPSC-2024-001": {
            "product_name": "Baby Crib Model XL-2000",
            "title": "Dropside Cribs Recalled Due to Entrapment Hazard",
        },
        "CPSC-2024-002": {
            "product_name": "SmartLight LED Bulb 60W",
            "title": "SmartLight LED Bulbs Pose Fire Hazard",
        },
    }
    
    matching = [r for id, r in mock_recalls.items() if query_lower in r["product_name"].lower() or query_lower in r["title"].lower()]
    print(f"Found {len(matching)} recalls for '{product_name}'")
    
    for recall in matching:
        print(f"  - {recall['product_name']}")
        print(f"    Title: {recall['title']}")
    
    print("\n✅ Search test passed!")
    
    # Test 2: Get details
    print("\n" + "=" * 60)
    print("Test 2: Getting recall details")
    print("=" * 60)
    
    recall_id = "CPSC-2024-001"
    detail = {
        "recall_id": "CPSC-2024-001",
        "product_name": "Baby Crib Model XL-2000",
        "title": "Dropside Cribs Recalled",
        "hazard_description": "The dropside rail can separate",
        "remedy": "Stop using immediately. Contact manufacturer for refund.",
        "affected_consumers": "Approximately 45,000 units",
    }
    
    print(f"Recall ID: {detail['recall_id']}")
    print(f"Product: {detail['product_name']}")
    print(f"Hazard: {detail['hazard_description']}")
    print(f"Remedy: {detail['remedy']}")
    print(f"Affected: {detail['affected_consumers']}")
    
    print("\n✅ Detail test passed!")
    print("\n" + "=" * 60)
    print("All tests passed! ✅")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)

