"""
Module for retrieving product information from Open Food Facts API.
"""
import requests

class ProductInfo:
    BASE_URL = "https://world.openfoodfacts.org/api/v0/product/"

    @staticmethod
    def get_product_info(barcode):
        """
        Fetch product information from Open Food Facts API.
        
        Args:
            barcode (str): Product barcode number
            
        Returns:
            dict: Product information if found, None otherwise
        """
        url = f"{ProductInfo.BASE_URL}{barcode}.json"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 1:  # Product found
                return data.get('product')
        return None