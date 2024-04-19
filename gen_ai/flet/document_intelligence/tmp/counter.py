import vertexai
import flet as ft
from vertexai.preview.generative_models import GenerativeModel, Part

def main(page: ft.Page):
    
    re = ft.Ref[ft.Column]()
    
    def add_clicked(e):
        page.add(ft.Checkbox(label=new_task.value))
        new_task.value = ""
        page.update()
        
    def llm(e):
        model = GenerativeModel("gemini-pro")
        responses = model.generate_content(
            new_task.value,
            generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.9,
            "top_p": 1
            },
            #stream=True,
            )
        _ = []
        
        re.current.controls.append(
            ft.Text(responses.candidates[0].content.parts[0].text, width=700, height=100)
        )
        
        #page.controls.append(ft.Text(f"{_[0]}"))
        
        page.update()

    new_task = ft.TextField(hint_text="Whats needs to be done?")

    page.add(new_task, 
             ft.ElevatedButton("Submit", on_click=llm),
             ft.Column(ref=re)
             )

ft.app(target=main, view=ft.AppView.WEB_BROWSER)



#%%
model = GenerativeModel("gemini-pro")
responses = model.generate_content(
    "What is machine learning?",
    generation_config={
    "max_output_tokens": 2048,
    "temperature": 0.9,
    "top_p": 1
    },
    #stream=True,
    )
_ = []

responses.candidates[0].content.parts[0].text

# %%
