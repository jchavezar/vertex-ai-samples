import asyncio
import os
import sys

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from regenerative_pipeline import run_regenerative_pipeline

async def test_pipeline():
    pdf_path = "../docs/08_HR_Compensation_Analysis_FY2024.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return
        
    prompt = "in the 1.2 column change the column names..."
    
    print(f"Running pipeline on {pdf_path}...")
    
    async for event in run_regenerative_pipeline(pdf_path, prompt):
        print(event.strip())

if __name__ == "__main__":
    asyncio.run(test_pipeline())
