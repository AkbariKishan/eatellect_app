"""
Barcode scanning tool using pyzbar and OpenCV.
"""
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from typing import Optional, List, Dict
from langchain_core.tools import tool


class BarcodeScanner:
    """Scanner for extracting barcodes from images."""
    
    @staticmethod
    def preprocess_image(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better barcode detection.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding for better contrast
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
    
    @staticmethod
    def scan_barcode_from_image(image_path: str) -> Optional[str]:
        """
        Extract barcode number from an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Barcode number as string, or None if no barcode found
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        # Try scanning original image first
        barcodes = decode(image)
        
        # If no barcode found, try with preprocessed image
        if not barcodes:
            preprocessed = BarcodeScanner.preprocess_image(image)
            barcodes = decode(preprocessed)
        
        # Extract first barcode found
        if barcodes:
            barcode_data = barcodes[0].data.decode('utf-8')
            barcode_type = barcodes[0].type
            print(f"Detected {barcode_type} barcode: {barcode_data}")
            return barcode_data
        
        return None
    
    @staticmethod
    def scan_multiple_barcodes(image_path: str) -> List[Dict[str, str]]:
        """
        Extract all barcodes from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing barcode data and type
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        barcodes = decode(image)
        
        results = []
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            results.append({
                "data": barcode_data,
                "type": barcode_type,
                "polygon": barcode.polygon
            })
        
        return results
    
    @staticmethod
    def scan_from_bytes(image_bytes: bytes) -> Optional[str]:
        """
        Extract barcode from image bytes (useful for API uploads).
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Barcode number as string, or None if no barcode found
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Could not decode image from bytes")
        
        barcodes = decode(image)
        
        if barcodes:
            return barcodes[0].data.decode('utf-8')
        
        return None


@tool
def extract_barcode_from_image(image_path: str) -> str:
    """
    Tool to extract barcode number from an image file.
    
    Args:
        image_path: Path to the image containing a barcode
        
    Returns:
        Barcode number as string
    """
    scanner = BarcodeScanner()
    barcode = scanner.scan_barcode_from_image(image_path)
    
    if not barcode:
        raise ValueError("No barcode detected in the image")
    
    return barcode
