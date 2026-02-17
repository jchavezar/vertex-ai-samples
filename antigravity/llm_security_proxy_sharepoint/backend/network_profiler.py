import sys
import time
import os
import requests
from markitdown import MarkItDown

def synthetic_latency_profile():
    print("=========================================")
    print("🌐 REAL-WORLD NETWORK & PARSING PROFILING")
    print("=========================================")
    
    # 1. Simulate API search/graph discovery
    url = "https://www.google.com"
    t0 = time.time()
    res = requests.get(url)
    t1 = time.time()
    print(f"1) Estimated External API Search Call: {t1 - t0:.2f}s")
    
    # 2. Download sample 16-page PDF (Arxiv paper or similar)
    pdf_url = "https://arxiv.org/pdf/1706.03762.pdf" # Attention is all you need
    t_down_start = time.time()
    resp = requests.get(pdf_url, stream=True)
    resp.raise_for_status()
    temp_filename = "attention.pdf"
    with open(temp_filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    t_down_end = time.time()
    print(f"2) Heavy Document Download (16 pages): {t_down_end - t_down_start:.2f}s")
    
    # 3. MarkItDown Transformation
    t_mid_start = time.time()
    md = MarkItDown()
    result = md.convert(temp_filename)
    t_mid_end = time.time()
    print(f"3) MarkItDown OCR/Parsing Latency:     {t_mid_end - t_mid_start:.2f}s")
    
    os.remove(temp_filename)
    
if __name__ == "__main__":
    synthetic_latency_profile()
