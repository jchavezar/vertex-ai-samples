import asyncio
from regenerative_pipeline import run_regenerative_pipeline
import os
import vertexai

vertexai.init(project=os.environ.get("PROJECT_ID", "vtxdemos"), location="global")

async def test():
    # Let's create a dummy pdf first
    pdf_path = "dummy.pdf"
    from weasyprint import HTML
    HTML(string="""
    <h1>1.2 Key Financial Highlights</h1>
    <p>Revenue: $100M</p>
    <p>Profit: $20M</p>
    <p>Loss: $5M</p>
    """).write_pdf(pdf_path)
    
    prompt = "with the 1.2 key financial highlights data generate a chart below"
    async for event in run_regenerative_pipeline(pdf_path, prompt):
        print(event)

asyncio.run(test())
