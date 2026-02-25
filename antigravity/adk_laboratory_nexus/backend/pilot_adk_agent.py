import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

# 🧠 Pilot: Design Consultant Agent
# This agent tests the distilled ADK documentation patterns.

class DesignAdvice(BaseModel):
    pillar: str = Field(description="The core design pillar (e.g. Palette, Typography, Motion)")
    suggestion: str = Field(description="Detailed suggestion based on Modern Cave style")
    implementation_hint: str = Field(description="Brief CSS or JS tip")

# Define the agent
design_bot = LlmAgent(
    name="modern_cave_consultant",
    model="gemini-3-flash-preview",
    instruction="""
    You are an expert UX consultant specializing in the 'Modern Cave' design system.
    Your style is neofuturistic, architectural, and monolithic.
    Use earthy tones, horizontal scroll journeys, and brutalist typography.
    Provide structured design advice.
    """,
    output_schema=DesignAdvice,
    output_key="advice"
)

def run_pilot():
    print("🚀 Initializing ADK Pilot Agent...")
    
    # Check for API Key
    if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("❌ Error: GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT must be set.")
        return

    # Initialize Runner (from google.adk.runners)
    runner = Runner(
        app_name="modern_cave_app",
        agent=design_bot,
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

    user_query = "How should I handle the transition between the hero and the bio section in a premium portfolio?"
    print(f"👤 User: {user_query}")
    
    try:
        # For ADK 1.23.0, Runner.run needs user_id, session_id, and new_message (types.Content)
        result = runner.run(
            user_id="test_user",
            session_id="test_session",
            new_message=types.Content(parts=[types.Part(text=user_query)], role="user")
        )
        
        final_text = ""
        last_session = None
        for event in result:
            if hasattr(event, 'text') and event.text:
                final_text = event.text
            if hasattr(event, 'session'):
                last_session = event.session

        # In some versions, the response is in a specific attribute of the last event
        # If advice is not in state, it might mean the agent hasn't finished or schema isn't populated yet.
        advice = last_session.state.get("advice") if last_session else None
        
        if advice:
            print("\n🗿 --- Modern Cave Consultant Advice ---")
            print(f"Pillar: {advice.get('pillar')}")
            print(f"Suggestion: {advice.get('suggestion')}")
            print(f"Code Hint: {advice.get('implementation_hint')}")
        else:
            print(f"\n🤖 Agent Response: {final_text}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Execution failed: {e}")

if __name__ == "__main__":
    run_pilot()
