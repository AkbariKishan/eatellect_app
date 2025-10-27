"""
Module for handling barcode scanning functionality using pyzbar and OpenCV.
"""
from pyzbar import pyzbar
import cv2

class BarcodeScanner:
    @staticmethod
    def scan_barcode_from_image(image_path):
        """
        Scan barcode from an image file.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Barcode number if found, None otherwise
        """
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect barcodes
        barcodes = pyzbar.decode(gray)

        # Process detected barcodes
        for barcode in barcodes:
            # Extract barcode data
            barcode_data = barcode.data.decode("utf-8")
            return barcode_data

        return None