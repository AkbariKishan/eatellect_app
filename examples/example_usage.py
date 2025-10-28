"""
Example: Analyze product from barcode image.
"""
from src.analyzer import AgenticHealthAnalyzer


def main():
    """Analyze product from barcode image."""
    
    # Initialize analyzer
    analyzer = AgenticHealthAnalyzer()
    
    # Analyze from barcode image
    image_path = "path/to/your/barcode_image.jpg"
    
    print("Scanning barcode and analyzing product...")
    result = analyzer.analyze_from_barcode_image(image_path)
    
    # Display results
    print(f"\n{'='*50}")
    print(f"Product: {result['product_name']}")
    print(f"Barcode: {result['barcode']}")
    print(f"Health Rating: {result['health_rating']}/10")
    print(f"\nConcerns: {', '.join(result['concerns'])}")
    print(f"\nAnalysis:\n{result['analysis']}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
