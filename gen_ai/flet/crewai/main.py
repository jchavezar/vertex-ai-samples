#%%
from flet import *
from crewai import Crew
from agents import AnalysisAgents
from tasks import AnalysisTasks


class AutonomousCrew:
    def __init__(self):
        pass

    def run(self, query: str):
        agents = AnalysisAgents()
        tasks = AnalysisTasks()

        search_analyst_agent = agents.search()
        research_task = tasks.research(search_analyst_agent, query)

        crew = Crew(
            agents=[
                search_analyst_agent,
            ],
            tasks=[
                research_task,
            ],
            verbose=True
        )

        result = crew.kickoff()
        return result

#%%

def main(page: Page):
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.vertical_alignment = MainAxisAlignment.CENTER

    crew = AutonomousCrew()

    def send_message(e):
        column: Column = Column(
            controls=[
                Text("User", style=TextStyle(size=14, color=colors.BLUE)),
                Container(
                    padding=10,
                    margin=10,
                    border_radius=15,
                    bgcolor="#1a3059",
                    content=Text(e.control.value))
            ]
        )
        display_message.content.controls.append(column)
        display_message.update()
        response = crew.run(e.control.value)
        display_message.content.controls.append(
            Column(
                controls=[
                    Text("Crew"),
                    Markdown(response, selectable=True)
                ]
            )
        )
        display_message.update()

    header: Container = Container(
        width=500,
        height=100,
        border=border.only(bottom=BorderSide(1, colors.GREY_500)),
        content=Image(src="google-cloud.svg", scale=0.5, fit=ImageFit.CONTAIN),
    )

    display_message: Container = Container(
        height=950,
        margin=10,
        border=border.all(1, colors.GREY_500),
        border_radius=5,
        bgcolor="#45474a",
        content=ListView(
            spacing=10,
            padding=10,
            auto_scroll=True
        )
    )

    text_input: Container = Container(
        margin=10,
        border=border.all(1, colors.GREY_500),
        border_radius=5,
        content=TextField(hint_text="Write something", on_submit=send_message),
    )

    main_container: Container = Container(
        bgcolor=colors.BLACK,
        height=1200,
        width=500,
        border=border.all(1, colors.GREY_500),
        border_radius=5,
        content=Column(
            controls=[
                header,
                display_message,
                text_input
            ]
        )
    )

    page.add(main_container)

app(target=main)