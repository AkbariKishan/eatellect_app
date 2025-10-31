"""
Tool for fetching product information from Open Food Facts API.
"""
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ProductResponse:
    """Container for product API response."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProductFetcher:
    """Fetcher for Open Food Facts API."""
    
    BASE_URL = "https://world.openfoodfacts.org/api/v2/product"
    
    @staticmethod
    def fetch_product_by_barcode(barcode: str) -> ProductResponse:
        """
        Fetch product information from Open Food Facts API.
        
        Args:
            barcode: Product barcode number
            
        Returns:
            ProductResponse object containing success status and data/error
        """
        url = f"{ProductFetcher.BASE_URL}/{barcode}.json"
        print("\n=== API Request Details ===")
        print(f"URL: {url}")
        print(f"Barcode: {barcode}")
        
        try:
            headers = {
                'User-Agent': 'Eatellect/1.0 (https://github.com/AkbariKishan/eatellect_app)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            print("\n=== API Response ===")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 404:
                return ProductResponse(success=False, error="Product not found")
            
            response.raise_for_status()
            data = response.json()
            
            print("\n=== Response Data ===")
            print(f"Status: {data.get('status')}")
            print(f"Status Verbose: {data.get('status_verbose', 'N/A')}")
            
            # Check if product was found
            if data.get("status") == 1 and "product" in data:
                product = data["product"]
                if not product:
                    return ProductResponse(success=False, error="Empty product data received")
                
                print("\n=== Product Details ===")
                print(f"Product Name: {product.get('product_name', 'Unknown')}")
                print(f"Brand: {product.get('brands', 'Unknown')}")
                print(f"Fields available: {list(product.keys())}")
                
                # Validate and clean product data
                cleaned_product = {
                    'product_name': product.get('product_name', 'N/A'),
                    'brands': product.get('brands', 'N/A'),
                    'image_url': product.get('image_url'),
                    'nutriments': product.get('nutriments', {}),
                    'ingredients_text': product.get('ingredients_text', ''),
                    'allergens': product.get('allergens_tags', []),
                    'categories': product.get('categories_tags', []),
                    'nutrition_grades': product.get('nutrition_grades'),
                    'ecoscore_grade': product.get('ecoscore_grade'),
                    'nova_group': product.get('nova_group'),
                }
                
                # Validate required fields
                if not cleaned_product['product_name'] and not cleaned_product['brands']:
                    return ProductResponse(success=False, error="Missing required product information")
                
                return ProductResponse(success=True, data=cleaned_product)
            else:
                return ProductResponse(success=False, error=f"Product not found. API Status: {data.get('status_verbose', 'Unknown')}")
                
        except requests.exceptions.RequestException as e:
            print(f"\n=== API Error ===\n{str(e)}")
            return ProductResponse(success=False, error=f"API request failed: {str(e)}")
        except Exception as e:
            print(f"\n=== Unexpected Error ===\n{str(e)}")
            return ProductResponse(success=False, error=f"Unexpected error: {str(e)}")


def fetch_product_info(barcode: str) -> dict:
    """
    Tool to fetch product information from Open Food Facts using barcode.
    
    Args:
        barcode: Product barcode number (EAN-13, UPC, etc.)
        
    Returns:
        Dictionary containing product information
    """
    fetcher = ProductFetcher()
    result = fetcher.fetch_product_by_barcode(barcode)
    
    if not result.success:
        raise ValueError(f"Failed to fetch product: {result.error}")
    
    return result.data