#!/usr/bin/env python3
"""
Main entry point for Eatellect Health Analyzer.
Simple CLI to analyze food products from barcode images or barcode numbers.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analyzer import AgenticHealthAnalyzer
from src.tools.barcode_scanner import BarcodeScanner
from src.tools.product_fetcher import ProductFetcher

from dotenv import load_dotenv  # ADD THIS

# Load environment variables from .env file
load_dotenv()  # ADD THIS

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header():
    """Print application header."""
    print("\n" + "="*60)
    print("🍎 EATELLECT - AI-Powered Food Health Analyzer")
    print("="*60 + "\n")


def print_results(result: dict):
    """
    Print analysis results in a formatted way.
    
    Args:
        result: Analysis results dictionary
    """
    print("\n" + "="*60)
    print("📊 HEALTH ANALYSIS REPORT")
    print("="*60)
    
    # Product Info
    print(f"\n📦 Product: {result.get('product_name', 'Unknown')}")
    print(f"🔢 Barcode: {result.get('barcode', 'N/A')}")
    
    # Health Rating
    rating = result.get('health_rating', 0)
    stars = "⭐" * rating + "☆" * (10 - rating)
    
    # Color code based on rating
    if rating >= 8:
        rating_label = "Excellent"
    elif rating >= 6:
        rating_label = "Good"
    elif rating >= 4:
        rating_label = "Moderate"
    else:
        rating_label = "Poor"
    
    print(f"\n💚 Health Rating: {rating}/10 - {rating_label}")
    print(f"   {stars}")
    
    # Nutritional Summary
    if result.get('nutritional_data'):
        print("\n📊 Key Nutritional Values (per 100g):")
        nutrition = result['nutritional_data']
        print(f"   • Energy: {nutrition.get('energy_100g', 0)} kcal")
        print(f"   • Protein: {nutrition.get('proteins_100g', 0)}g")
        print(f"   • Carbs: {nutrition.get('carbohydrates_100g', 0)}g")
        print(f"   • Sugar: {nutrition.get('sugars_100g', 0)}g")
        print(f"   • Fat: {nutrition.get('fat_100g', 0)}g")
        print(f"   • Fiber: {nutrition.get('fiber_100g', 0)}g")
    
    # Concerns
    if result.get('concerns'):
        print("\n⚠️  Health Concerns:")
        for concern in result['concerns']:
            print(f"   • {concern}")
    else:
        print("\n✅ No major health concerns detected")
    
    # Detailed Analysis
    if result.get('analysis'):
        print("\n🔍 Detailed Analysis:")
        print("-" * 60)
        print(result['analysis'])
        print("-" * 60)
    
    # Recommendations
    if result.get('recommendations'):
        print("\n💡 Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    print("\n" + "="*60 + "\n")


def analyze_from_image(image_path: str):
    """
    Execute workflow: Scan barcode from image and analyze product.
    
    Args:
        image_path: Path to barcode image
    """
    print(f"📸 Scanning barcode from image: {image_path}\n")
    
    try:
        # Initialize analyzer
        analyzer = AgenticHealthAnalyzer()
        
        print("⚙️  Executing agentic workflow...")
        print("   → Scanning barcode...")
        print("   → Fetching product data...")
        print("   → Analyzing nutritional content...")
        print("   → Generating recommendations...\n")
        
        # Execute workflow
        result = analyzer.analyze_from_barcode_image(image_path)
        
        # Display results
        print_results(result)
        
        return result
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def analyze_from_barcode(barcode: str):
    """
    Execute workflow: Fetch product by barcode and analyze.
    
    Args:
        barcode: Product barcode number
    """
    print(f"🔍 Fetching product for barcode: {barcode}\n")
    
    try:
        # Fetch product info
        print("⚙️  Executing workflow...")
        print("   → Fetching product data from Open Food Facts...")
        
        fetcher = ProductFetcher()
        product_info = fetcher.fetch_product_by_barcode(barcode)
        
        if not product_info:
            print(f"❌ No product found for barcode: {barcode}")
            print("💡 Try scanning from an image instead or check the barcode number")
            sys.exit(1)
        
        print(f"   ✓ Product found: {product_info.get('product_name', 'Unknown')}")
        print("   → Analyzing nutritional content...")
        print("   → Generating recommendations...\n")
        
        # Initialize analyzer and execute
        analyzer = AgenticHealthAnalyzer()
        result = analyzer.analyze_product(product_info, barcode)
        
        # Display results
        print_results(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def interactive_mode():
    """
    Interactive mode - prompt user for input.
    """
    print_header()
    print("Choose an option:")
    print("  1. Analyze from barcode image")
    print("  2. Analyze from barcode number")
    print("  3. Exit\n")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        image_path = input("\nEnter path to barcode image: ").strip()
        if not os.path.exists(image_path):
            print(f"❌ Error: File not found: {image_path}")
            sys.exit(1)
        analyze_from_image(image_path)
        
    elif choice == "2":
        barcode = input("\nEnter barcode number: ").strip()
        if not barcode:
            print("❌ Error: Barcode cannot be empty")
            sys.exit(1)
        analyze_from_barcode(barcode)
        
    elif choice == "3":
        print("👋 Goodbye!")
        sys.exit(0)
        
    else:
        print("❌ Invalid choice. Please enter 1, 2, or 3")
        sys.exit(1)


def main():
    """
    Main entry point with command-line argument handling.
    """
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set")
        print("\nPlease set it:")
        print("  export GROQ_API_KEY='your_api_key_here'")
        print("or create a .env file with:")
        print("  GROQ_API_KEY=your_api_key_here\n")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # No arguments - run interactive mode
        interactive_mode()
        
    elif len(sys.argv) == 2:
        # Single argument - treat as image path
        arg = sys.argv[1]
        
        if arg in ["-h", "--help", "help"]:
            print_header()
            print("Usage:")
            print("  python main.py                    # Interactive mode")
            print("  python main.py <image_path>       # Analyze from image")
            print("  python main.py -b <barcode>       # Analyze from barcode")
            print("\nExamples:")
            print("  python main.py barcode.jpg")
            print("  python main.py -b 3017620422003")
            print("  python main.py --help\n")
            sys.exit(0)
        
        print_header()
        analyze_from_image(arg)
        
    elif len(sys.argv) == 3 and sys.argv[1] in ["-b", "--barcode"]:
        # Barcode flag with value
        print_header()
        analyze_from_barcode(sys.argv[2])
        
    else:
        print("❌ Invalid arguments. Use 'python main.py --help' for usage")
        sys.exit(1)


if __name__ == "__main__":
    main()
