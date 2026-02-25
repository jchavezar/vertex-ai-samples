import os
import asyncio
import json
import random
from typing import AsyncGenerator
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.protocol import AIStreamProtocol
from src.schemas import AgentBlock, ChartWidget, TextResponse, StatsWidget, DataPoint, StatItem

load_dotenv()

# Simulation Mode (if no API Key present)
USE_MOCK = os.getenv("GOOGLE_API_KEY") is None

class StockAgent:
    def __init__(self):
        if not USE_MOCK:
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model_id = "gemini-2.5-flash" # Or 1.5-flash / 3.0-pro-preview
        else:
            print("WARNING: No GOOGLE_API_KEY found. Running in MOCK mode.")

    async def generate_stream(self, messages: list) -> AsyncGenerator[str, None]:
        """
        Generates a stream of AIStreamProtocol events based on the conversation history.
        """
        last_message = messages[-1]['content']
        
        # --- MOCK MODE LOGIC (Robust Fallback) ---
        if USE_MOCK:
            yield AIStreamProtocol.text("I am running in MOCK MODE (No API Key found).\n")
            await asyncio.sleep(0.5)
            
            if "chart" in last_message.lower() or "price" in last_message.lower():
                yield AIStreamProtocol.text("Generating a simulated chart for you...\n")
                await asyncio.sleep(1)
                
                # Mock Chart Data
                mock_chart = ChartWidget(
                    title="Mock Apple Inc. (AAPL)",
                    chart_type="line",
                    ticker="AAPL",
                    data=[
                        DataPoint(label="Jan", value=150.0),
                        DataPoint(label="Feb", value=155.0),
                        DataPoint(label="Mar", value=160.0),
                        DataPoint(label="Apr", value=158.0),
                        DataPoint(label="May", value=170.0)
                    ]
                )
                yield AIStreamProtocol.data(mock_chart.model_dump())
                
            else:
                yield AIStreamProtocol.text(f"You said: {last_message}. Ask me for a 'chart' to see the widget protocol in action.")
            return

        # --- REAL GEMINI LOGIC ---
        try:
            # 1. Define the Config with Structured Output Schema
            # We want the model to act as a structured component generator
            prompt = f"""
            You are an advanced Stock Terminal Assistant.
            Your goal is to answer the user request using a mix of Text and UI Widgets.
            
            User Query: {last_message}
            
            AVAILABLE WIDGETS:
            1. ChartWidget: For visualizing trends (line) or comparisons (bar/pie).
            2. StatsWidget: For showing key financial metrics (P/E, Market Cap).
            
            INSTRUCTIONS:
            - Always prefer returning a ChartWidget if the user asks for prices, history, or comparisons.
            - Use TextResponse for explanations.
            - You can mix them. For example, Text -> Chart -> Text.
            """

            # We stream the raw text first to keep latency low, 
            # BUT for complex widgets, we might need a 2-step approach or use function calling.
            # Strategy: We will use a standard content generation stream, and if we detect specific triggers 
            # or if we use function calling, we format them.
            
            # Simplified Strategy for Stability: 
            # We will use 'generate_content_stream' without strict JSON enforcement for the *chat* part,
            # but we will use a TOOL for the chart generation.
            
            # Define a tool for creating charts
            def create_chart(title: str, chart_type: str, data_points: list[dict]):
                """Generates a chart widget for the dashboard."""
                # In a real agent, this might fetch data. 
                # Here, the LLM provides the data via the tool args.
                return "Chart generated successfully."

            # Mock data fetcher tool to give the LLM real-ish numbers to plot
            def get_stock_history(ticker: str):
                """Get historical prices for a ticker."""
                # Return dummy data for the LLM to process
                import random
                base = 100 + len(ticker)
                return [{"date": f"2024-01-{i:02d}", "price": base + random.randint(-5, 5)} for i in range(1, 10)]

            tools = [get_stock_history]
            
            # Generate Stream
            response = self.client.models.generate_content_stream(
                model=self.model_id,
                contents=[last_message],
                config=types.GenerateContentConfig(
                    tools=tools,
                    system_instruction="You are a stock terminal. Use `get_stock_history` if you need data. Then Describe the chart you want to draw.",
                    temperature=0.7
                )
            )

            async for chunk in response:
                # 1. Handle Function Calls (The LLM wants to run a tool)
                for part in chunk.candidates[0].content.parts:
                    if part.function_call:
                        fn = part.function_call
                        call_id = "call_" + str(random.randint(1000, 9999))
                        yield AIStreamProtocol.tool_call(call_id, fn.name, fn.args)
                        
                        # Execute Tool (Client-side execution simulation or server-side)
                        # For this demo, we execute server-side immediately and stream result
                        if fn.name == "get_stock_history":
                            result = get_stock_history(fn.args['ticker'])
                            yield AIStreamProtocol.tool_result(call_id, fn.name, result)
                            
                            # After getting data, the LLM usually continues to explain it.
                            # We might want to explicitly push a Chart Widget here based on the data.
                            # For this demo, we'll auto-convert the result to a Chart Widget protocol 
                            # to demonstrate the 'Data' channel.
                            
                            chart_data = [DataPoint(label=d['date'], value=d['price']) for d in result]
                            widget = ChartWidget(
                                title=f"{fn.args['ticker']} History",
                                chart_type="line",
                                ticker=fn.args['ticker'],
                                data=chart_data
                            )
                            yield AIStreamProtocol.data(widget.model_dump())

                    if part.text:
                        yield AIStreamProtocol.text(part.text)

        except Exception as e:
            print(f"Agent Error: {e}")
            yield AIStreamProtocol.text(f"Error: {str(e)}")
