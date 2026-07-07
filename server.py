"""
Recall Checker MCP Server - Check for product recalls
Tools:
  1. check_recalls: Search for active recalls on a product
  2. get_recall_details: Get full details on a specific recall

Note: v1 uses mock data. Real CPSC API integration coming when API access is resolved.
"""

from mcp.server import FastMCP
import requests
from typing import Optional
from pydantic import BaseModel, Field

# Initialize the MCP server
mcp = FastMCP("Recall Checker")

# Mock recall database (v1) - Replace with CPSC API once endpoint access is resolved
MOCK_RECALLS = {
    "CPSC-2024-001": {
        "recall_id": "CPSC-2024-001",
        "product_name": "Baby Crib Model XL-2000",
        "title": "Dropside Cribs Recalled Due to Entrapment Hazard",
        "hazard_description": "The dropside rail can separate, posing an entrapment hazard to infants.",
        "product_description": "Wooden baby cribs with dropside rails manufactured 2020-2024",
        "date_announced": "2024-03-15",
        "remedy": "Stop using immediately. Contact manufacturer for full refund or safety bar replacement kit.",
        "affected_consumers": "Approximately 45,000 units",
    },
    "CPSC-2024-002": {
        "recall_id": "CPSC-2024-002",
        "product_name": "SmartLight LED Bulb 60W",
        "title": "SmartLight LED Bulbs Pose Fire Hazard Due to Overheating",
        "hazard_description": "The LED driver can overheat and cause the bulb to ignite.",
        "product_description": "Smart WiFi LED bulbs compatible with Alexa, 60W equivalent, models SL-60W and SL-60WX",
        "date_announced": "2024-02-20",
        "remedy": "Stop using immediately. Return to retailer for full refund.",
        "affected_consumers": "Approximately 120,000 units",
    },
    "CPSC-2024-003": {
        "recall_id": "CPSC-2024-003",
        "product_name": "ToyBlock Building Set",
        "title": "Children's Building Blocks Recalled Due to Small Magnet Hazard",
        "hazard_description": "Small magnets can detach and be swallowed by children, posing serious internal injury risk.",
        "product_description": "Magnetic building block sets for ages 5+, models TB-100, TB-200, TB-300",
        "date_announced": "2024-01-10",
        "remedy": "Contact manufacturer for prepaid return label. Full refund issued.",
        "affected_consumers": "Approximately 85,000 units",
    },
}


class RecallSummary(BaseModel):
    """Brief recall summary"""
    recall_id: str = Field(description="Unique recall ID")
    product_name: str = Field(description="Product name")
    title: str = Field(description="Recall title")
    hazard_description: str = Field(description="What's the hazard")
    date_announced: str = Field(description="When the recall was announced")


class RecallDetails(BaseModel):
    """Full recall details"""
    recall_id: str = Field(description="Unique recall ID")
    product_name: str = Field(description="Product name")
    title: str = Field(description="Recall title")
    hazard_description: str = Field(description="Hazard description")
    product_description: str = Field(description="Product description")
    date_announced: str = Field(description="Announcement date")
    remedy: str = Field(description="Remedy/action consumers should take")
    affected_consumers: str = Field(description="Number/description of affected units")


@mcp.tool()
def check_recalls(product_name: str) -> list[RecallSummary]:
    """
    Search for active recalls on a product
    
    Args:
        product_name: Product name to search for (e.g., "baby crib", "LED bulb", "building blocks")
        
    Returns:
        List of active recalls matching the product
    """
    try:
        product_lower = product_name.lower()
        matching_recalls = []
        
        # Search mock database
        for recall_id, recall_data in MOCK_RECALLS.items():
            if (product_lower in recall_data["product_name"].lower() or
                product_lower in recall_data["title"].lower() or
                product_lower in recall_data["hazard_description"].lower()):
                matching_recalls.append(
                    RecallSummary(
                        recall_id=recall_data["recall_id"],
                        product_name=recall_data["product_name"],
                        title=recall_data["title"],
                        hazard_description=recall_data["hazard_description"],
                        date_announced=recall_data["date_announced"],
                    )
                )
        
        return matching_recalls
        
    except Exception as e:
        raise ValueError(f"Failed to search recalls: {str(e)}")


@mcp.tool()
def get_recall_details(recall_id: str) -> RecallDetails:
    """
    Get full details on a specific recall by ID
    
    Args:
        recall_id: Recall ID (from check_recalls results, e.g., "CPSC-2024-001")
        
    Returns:
        Full recall details with remedy information
    """
    try:
        if recall_id not in MOCK_RECALLS:
            raise ValueError(f"Recall ID '{recall_id}' not found")
        
        recall_data = MOCK_RECALLS[recall_id]
        
        return RecallDetails(
            recall_id=recall_data["recall_id"],
            product_name=recall_data["product_name"],
            title=recall_data["title"],
            hazard_description=recall_data["hazard_description"],
            product_description=recall_data["product_description"],
            date_announced=recall_data["date_announced"],
            remedy=recall_data["remedy"],
            affected_consumers=recall_data["affected_consumers"],
        )
        
    except KeyError as e:
        raise ValueError(f"Recall not found: {recall_id}")
    except Exception as e:
        raise ValueError(f"Error fetching recall details: {str(e)}")


if __name__ == "__main__":
    mcp.run()
