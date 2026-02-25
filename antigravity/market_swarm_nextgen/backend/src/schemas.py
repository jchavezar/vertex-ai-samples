from pydantic import BaseModel, Field
from typing import List, Literal, Union, Optional, Dict, Any

# --- Widget Schemas ---
# These schemas define what the Frontend can render.

class DataPoint(BaseModel):
    label: str = Field(description="The x-axis label (date, category, etc.)")
    value: float = Field(description="The y-axis value")
    tooltip: Optional[str] = Field(None, description="Optional tooltip text")

class ChartWidget(BaseModel):
    type: Literal["chart"] = "chart"
    title: str = Field(..., description="Title of the chart")
    chart_type: Literal["line", "bar", "pie", "area"] = Field(..., description="Type of chart to render")
    data: List[DataPoint] = Field(..., description="The data points for the chart")
    ticker: Optional[str] = Field(None, description="Associated ticker symbol")

class StatItem(BaseModel):
    label: str
    value: str
    trend: Optional[Literal["up", "down", "neutral"]] = None

class StatsWidget(BaseModel):
    type: Literal["stats"] = "stats"
    title: str = Field(..., description="Title of the stats panel")
    items: List[StatItem] = Field(..., description="List of key statistics")

# --- Agent Response Schema ---
# The Agent will output a structure matching this union.

class AgentThinking(BaseModel):
    type: Literal["thinking"] = "thinking"
    content: str = Field(..., description="Internal reasoning or status update")

class TextResponse(BaseModel):
    type: Literal["text"] = "text"
    content: str = Field(..., description="The conversational response to the user")

# Union of all possible blocks the agent can generate
class AgentBlock(BaseModel):
    # We use a wrapper to allow the agent to return a list of heterogeneous blocks
    blocks: List[Union[ChartWidget, StatsWidget, TextResponse, AgentThinking]]

