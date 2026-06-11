from paddleocr import PaddleOCR
import logging

logging.basicConfig(level=logging.INFO)
print("Initializing PaddleOCR to download models...")
try:
    ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=True)
    print("Models downloaded successfully!")
except Exception as e:
    print(f"Error: {e}")
