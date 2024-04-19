# Import the flet module
import vertexai
import flet as ft
from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part


# Define a class called Chat that is a subclass of ft.UserControl
class Chat(ft.UserControl):

    def build(self):
        # Create a heading text element
        self.heading = ft.Text(value="Gemini Pro Chatbot", size=24)
        
        # Create a text input field for user prompts
        self.text_input = ft.TextField(hint_text="Enter your prompt", expand=True, on_submit=self.btn_clicked)
        
        # Create an empty column to hold the output elements
        self.output_column = ft.Column()
        
        # Enable scrolling in the chat interface
        self.scroll = True
        
        # Dropdown to selcet the model
        self.dd = ft.Dropdown(
        options=[
            ft.dropdown.Option("gemini-pro"),
            ft.dropdown.Option("text-bison@002"),
            ft.dropdown.Option("text-bison32k@002"),
        ],
        width=200,
        )
        
        # Create the layout of the chat interface using the ft.Column container
        return ft.Column(
            width=800,
            controls=[
                # Add the heading, text input, and submit button in a row
                self.heading,
                ft.Row(
                    controls=[
                        self.dd,
                        self.text_input,
                        ft.ElevatedButton("Submit", height=60, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=1)), on_click=self.btn_clicked),
                    ],
                ),
                # Add the output column to display the chatbot responses
                self.output_column,
            ],
        )
    
    def btn_clicked(self, event):
        # Send the user input to the llm API for completion
        
        if self.dd.value == "gemini-pro":
            model = GenerativeModel("gemini-pro")
            responses = model.generate_content(
                self.text_input.value,
                generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.9,
                "top_p": 1
                },
                #stream=True,
                )

            # Get the output text from the API response
            self.output = responses.candidates[0].content.parts[0].text
            
        else:
            vertexai.init(project="vtxdemos", location="us-central1")
            parameters = {
                "candidate_count": 1,
                "max_output_tokens": 1024,
                "temperature": 0.9,
                "top_p": 1
            }
            model = TextGenerationModel.from_pretrained("text-bison@002")
            response = model.predict(
                self.text_input.value,
                **parameters
            )
            self.output = response.text
        
        # Create a new Output object to display the chatbot response
        result = Output(self.output, self.text_input.value, self.outputDelete)
        
        # Add the Output object to the output column
        self.output_column.controls.append(result)
        
        # Clear the text input field
        self.text_input.value = ""
        
        # Update the page to reflect the changes
        self.update()

    def outputDelete(self, result):
        # Remove the specified result from the output column
        self.output_column.controls.remove(result)
        
        # Update the page to reflect the changes
        self.update()


# Define a class called Output that is a subclass of ft.UserControl
class Output(ft.UserControl):
    def __init__(self, myoutput, mytext_input, myoutput_delete):
        super().__init__()
        self.myoutput = myoutput 
        self.mytext_input = mytext_input
        self.myoutput_delete = myoutput_delete

    def build(self):
        # Create a text element to display the chatbot response
        self.output_display = ft.Text(value=self.myoutput, selectable=True, width=700, )
        
        # Create a delete button to remove the chatbot response
        self.delete_button = ft.IconButton(ft.icons.DELETE_OUTLINE_SHARP, on_click=self.delete)
        
        # Create a container to display the user input
        self.input_display = ft.Container(
            content=ft.Text(value=self.mytext_input),
            padding=10,
            #margin=5,
            width=300,
            bgcolor=ft.colors.BLUE,
            border_radius=10,
            alignment=ft.alignment.Alignment(-0.5, -0.5)
            )        
        # Create a column layout to arrange the elements
        self.display_view = ft.Column(controls=[self.input_display, self.output_display, self.delete_button])

        # Return the column layout as the UI representation of the Output class
        return self.display_view

    def delete(self, e):
        # Call the outputDelete function with the current instance as an argument
        self.myoutput_delete(self)


# Define a main function that sets up the page layout
def main(page):
    page.scroll = True
    page.window_width = 500
    page.window_height = 700
    page.theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.colors.GREEN,
        primary_container=ft.colors.GREEN_200
        # ...
    ),
)
    
    # Create a new Chat object
    mychat = Chat()
    
    # Add the Chat object to the page
    page.add(mychat)


# Run the application using the ft.app() function and pass the main function as the target
ft.app(target=main, view=ft.AppView.WEB_BROWSER)