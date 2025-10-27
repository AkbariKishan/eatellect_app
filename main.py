"""
Main application module combining barcode scanning, product info retrieval, and AI analysis.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from src.barcode_scanner import BarcodeScanner
from src.product_info import ProductInfo
from src.health_analyzer import HealthAnalyzer

def main():
    # Load environment variables from .env file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path, override=True)  # Make sure to override existing env variables
    
    # Initialize components
    analyzer = HealthAnalyzer()

    while True:
        # Get image path from user
        image_path = input("Enter the path to the product image (or 'quit' to exit): ")
        
        if image_path.lower() == 'quit':
            break

        try:
            # Scan barcode
            barcode = BarcodeScanner.scan_barcode_from_image(image_path)
            if not barcode:
                print("No barcode found in the image.")
                continue

            # Get product information
            product_info = ProductInfo.get_product_info(barcode)
            if not product_info:
                print(f"No product information found for barcode: {barcode}")
                continue

            # Analyze product health information
            health_analysis = analyzer.analyze_product(product_info)
            print("\nHealth Analysis:")
            print("---------------")
            print(health_analysis)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
