try:
    import fitz
    print("fitz OK")
except Exception as e:
    print("fitz FAIL:", e)

try:
    from paddleocr import PaddleOCR
    print("paddleocr OK")
except Exception as e:
    print("paddleocr FAIL:", e)
