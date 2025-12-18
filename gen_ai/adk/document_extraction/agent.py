from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from pydantic import BaseModel, Field
from typing import List

# Define the schema for a single item on the receipt
class LineItem(BaseModel):
    description: str = Field(description="Description of the purchased item.")
    quantity: int = Field(description="Quantity of the purchased item.")
    price: float = Field(description="Price of a single unit of the item.")
    total_price: float = Field(description="Total price for the line item (quantity * price).")

# Define the main schema for the extracted receipt information
class ReceiptSchema(BaseModel):
    """Represents the structured information extracted from a receipt."""
    merchant_name: str = Field(description="The name of the merchant or store.")
    merchant_address: str = Field(description="The address of the merchant.")
    merchant_website: str = Field(description="The official website of the merchant, found using Google Search.")
    transaction_date: str = Field(description="The date of the transaction (e.g., YYYY-MM-DD).")
    transaction_time: str = Field(description="The time of the transaction (e.g., HH:MM:SS).")
    line_items: List[LineItem] = Field(description="A list of all items purchased.")
    subtotal: float = Field(description="The subtotal amount before tax or tip.")
    tax: float = Field(description="The total tax amount.")
    tip: float = Field(description="The tip or gratuity amount.")
    total_amount: float = Field(description="The final total amount paid.")
    payment_method: str = Field(description="The method of payment (e.g., 'Credit Card', 'Cash').")

# Define the agent for document extraction
root_agent = Agent(
    name="document_extraction_agent",
    model="gemini-3-flash-preview",
    description="An AI agent that extracts structured information from receipts and can search the web.",
    instruction="""Your task is to act as a highly accurate document parser.
When a file is uploaded, you must analyze its content, which will be a receipt.
Extract all relevant information from the receipt and populate the fields of the `ReceiptSchema`.

After extracting the merchant's name, you MUST use the Google Search tool to find the official website for that merchant and populate the `merchant_website` field.

If any other piece of information is not available on the receipt, leave the corresponding field empty.
    """,
    tools=[GoogleSearchTool()],
    output_schema=ReceiptSchema
)
