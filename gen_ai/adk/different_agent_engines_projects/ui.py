#%%
import colorsys
from email.policy import default

from flet import *
import asyncio
import google.adk.sessions
from vertexai import agent_engines

agent_engine_1 = "projects/254356041555/locations/us-central1/reasoningEngines/3217879108360863744" # Output from deploy_agent_engine.py
agent_engine_2 = "projects/722330367743/locations/us-central1/reasoningEngines/613672623833874432" # Output from deploy_agent_engine.py

agent_engine_1 = agent_engines.get(agent_engine_1)
agent_engine_2 = agent_engines.get(agent_engine_2)
# asyncio.run(send_message("What's going on in mlb now?", remote_app=agent_engine_1))
# asyncio.run(send_message("what are the latest news?", remote_app=agent_engine_2))

agent = agent_engine_1

def main(page: Page):
    page.horizontal_alignment="center"
    MAIN_WIDTH = 500
    colors = [
        {"color": Colors.RED, "value": "sports_agent"},
        {"color": Colors.BLUE, "value": "news_agent"},

    ]
    def get_options(
    ):
        options = []
        for color in colors:
            options.append(
                DropdownOption(
                    key=color["value"],
                    content=Text(
                        value=color["value"],
                        color=color["color"],
                    )
                )
            )
        return options

    def dropdown_changed(e):
        global agent
        if e.control.value == "sports_agent":
            agent = agent_engine_1
        else:
            agent = agent_engine_2
        page.update()

    async def send_message(e):
        session = await agent.async_create_session(user_id="u_123")
        print(session["id"])
        async for event in agent.async_stream_query(
                user_id="u_123",
                session_id=session.id if isinstance(session, google.adk.sessions.Session) else session["id"],
                message=e.control.value
        ):
            print(event)
            print(type(event))
            print(event["content"]["parts"][0]["text"])
            main_chat.controls.append(Text(event["content"]["parts"][0]["text"], color=Colors.YELLOW))
            page.update()

    page.add(
        Column(
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            controls=[
                Container(
                    content=Dropdown(
                        label="agent",
                        value="sports_agent",
                        options=get_options(),
                        border_color=Colors.TRANSPARENT,
                        on_change=dropdown_changed,
                    ),
                    border_radius=12.0,
                    padding=5.0,
                    border=border.all(1, Colors.GREY)
                ),
                Container(
                    main_chat:=ListView(
                        controls=[
                        ]
                    ),
                    border_radius=12.0,
                    height=400,
                    padding=5.0,
                    width=MAIN_WIDTH,
                    border=border.all(1, Colors.GREY)
                ),
                Container(
                    padding=5.0,
                    content=TextField(
                        label="Input",
                        border_color=Colors.TRANSPARENT,
                        on_submit=send_message,
                    ),
                    border_radius=12.0,
                    width=MAIN_WIDTH,
                    border=border.all(1, Colors.GREY)
                )
            ]
        )
    )

app(target=main)