import os
from typing import List, Any, Optional
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.genai import types

# Model IDs based on USER_REQUEST
GEMINI_3_PRO = "projects/vtxdemos/locations/global/publishers/google/models/gemini-3-pro-preview"
GEMINI_3_FLASH = "projects/vtxdemos/locations/global/publishers/google/models/gemini-3-flash-preview"
GEMINI_2_5_PRO = "gemini-2.5-pro"
GEMINI_2_5_FLASH = "gemini-2.5-flash"

# --- Schemas ---

class BoundingBox(BaseModel):
    ymin: float = Field(description="Normalized Y coordinate (0-1000) for top")
    xmin: float = Field(description="Normalized X coordinate (0-1000) for left")
    ymax: float = Field(description="Normalized Y coordinate (0-1000) for bottom")
    xmax: float = Field(description="Normalized X coordinate (0-1000) for right")

class ChartObject(BaseModel):
    label: str = Field(description="Label or name of the object identified inside the chart")
    text_confidence: float = Field(description="Confidence score for the text/label extracted (0.0 to 1.0)", default=1.0)
    bounding_box: BoundingBox = Field(description="Bounding box of this specific object within the chart")

class ChartData(BaseModel):
    headers: List[str] = Field(description="Column headers of the extracted table")
    rows: List[List[Any]] = Field(description="Data rows corresponding to the headers")

class ChartExtraction(BaseModel):
    page_number: int = Field(description="Page number where the chart was found")
    chart_bounding_box: BoundingBox = Field(description="Bounding box of the entire chart/diagram on the PDF page")
    description: str = Field(description="A very detailed, precise, and lengthy description of the chart/diagram.")
    confidence: float = Field(description="Confidence level of the overall chart extraction (0.0 to 1.0)")
    objects_inside: List[ChartObject] = Field(description="List of distinct objects found inside the chart with their bounding boxes and label confidence")
    extracted_data: Optional[ChartData] = Field(description="Structured tabular data extracted from the chart")

class TableExtraction(BaseModel):
    page_number: int = Field(description="Page number where the table was found")
    table_bounding_box: BoundingBox = Field(description="Bounding box of the table on the PDF page")
    description: str = Field(description="A detailed description of the table's purpose and content.")
    confidence: float = Field(description="Confidence level of the extraction (0.0 to 1.0)")
    extracted_data: ChartData = Field(description="Structured tabular data")

class PdfExtractionResult(BaseModel):
    charts: List[ChartExtraction] = Field(description="List of all charts/diagrams found in the PDF")
    tables: List[TableExtraction] = Field(description="List of all standalone tables found in the PDF", default_factory=list)

# --- Agent Factories ---

def create_page_extractor_agent(page_num: int, model_id: str = GEMINI_3_FLASH) -> Agent:
    """Factory to create an agent focused on a specific page with a configurable model."""
    return Agent(
        name=f"page_{page_num}_extractor",
        model=model_id,
        description=f"Expert extractor focusing on PDF page {page_num}.",
        instruction=f"""
        Analyze the provided image of Page {page_num} and:
        1. Identify any charts, diagrams, or standalone tables.
        2. Provide normalized bounding boxes (0-1000).
        3. Describe each element in extreme detail.
        4. Extract tabular data if present.
        5. Assign confidence scores (0.0-1.0) to elements and labels.
        """,
        output_schema=PdfExtractionResult
    )

def create_evaluator_agent(model_id: str = GEMINI_3_FLASH) -> Agent:
    """Factory for evaluator agent."""
    return Agent(
        name="quality_evaluator",
        model=model_id,
        description="Evaluates extraction quality.",
        instruction="Review the extracted data for consistency, confidence and bounding box accuracy. Provide a quality summary."
    )
