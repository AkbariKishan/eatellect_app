"""
Tool for fetching product information from Open Food Facts API.
"""
import requests
from typing import Optional, Dict
from langchain_core.tools import tool


class ProductFetcher:
    """Fetcher for Open Food Facts API."""
    
    BASE_URL = "https://world.openfoodfacts.org/api/v2/product"
    
    @staticmethod
    def fetch_product_by_barcode(barcode: str) -> Optional[Dict]:
        """
        Fetch product information from Open Food Facts API.
        
        Args:
            barcode: Product barcode number
            
        Returns:
            Product information dictionary, or None if not found
        """
        url = f"{ProductFetcher.BASE_URL}/{barcode}.json"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if product was found
            if data.get("status") == 1:
                return data.get("product", {})
            else:
                print(f"Product not found for barcode: {barcode}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching product data: {e}")
            return None
    
    @staticmethod
    def fetch_with_fields(barcode: str, fields: list) -> Optional[Dict]:
        """
        Fetch specific fields from Open Food Facts API.
        
        Args:
            barcode: Product barcode number
            fields: List of field names to retrieve
            
        Returns:
            Product information with only requested fields
        """
        fields_param = ",".join(fields)
        url = f"{ProductFetcher.BASE_URL}/{barcode}.json?fields={fields_param}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == 1:
                return data.get("product", {})
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching product data: {e}")
            return None


@tool
def fetch_product_info(barcode: str) -> dict:
    """
    Tool to fetch product information from Open Food Facts using barcode.
    
    Args:
        barcode: Product barcode number (EAN-13, UPC, etc.)
        
    Returns:
        Dictionary containing product information
    """
    fetcher = ProductFetcher()
    product_info = fetcher.fetch_product_by_barcode(barcode)
    
    if not product_info:
        raise ValueError(f"No product found for barcode: {barcode}")
    
    return product_info
