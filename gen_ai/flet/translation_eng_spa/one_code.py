import json
import queue
import vertexai
import threading
from flet import *
from anthropic import AnthropicVertex
from vertexai.generative_models import GenerativeModel

project_id = "vtxdemos"
vertex_location = "us-central1"
claude_location = "us-east5"
claude_model = "claude-3-5-sonnet-v2@20241022"
gemini_model = "gemini-1.5-pro-002"

ant_client = AnthropicVertex(project_id=project_id, region=claude_location)
vertexai.init(project=project_id, location=vertex_location)
result_queue = queue.Queue()

system_instruction = """
You are a Spanish Linguistic Expert that works for The New York Times as a Columnist. Your task is to translate the following text into Mexican Spanish, with the intent to be published for people in Mexico.                

### Rules:
- **Accuracy is key**: The translation needs to be accurate without missing any important part of the context of the paragraph.
- **Formal Tone**: Maintain a formal tone that is also accessible and engaging for a Mexican audience.
- **Idioms**: Detect and use idioms when appropriate. Never do a literal translation of idioms. Refer to the examples provided for guidance. Be aware of regional variations in Mexican Spanish and choose the most suitable idiom for a general audience.
- **Gender Carefulness**: Read the context of the entire text and never miss the gender of the spoken subject.
- **Avoid Literal Translation**: If a phrase sounds unnatural or awkward in a direct translation, opt for a more contextual translation without missing the accuracy of the meaning in the sentence.
- **Natural Flow and Style**: Ensure the translated text flows naturally and adheres to the specific style and tone expected for a The New York Times column.
- **Cultural Nuances**: Where appropriate, adapt the translation to reflect Mexican cultural references and sensitivities.  

### Idiom Examples:
- Piece of cake: pan comido
- To be in hot water: estar en apuros
- To hit the nail on the head: Dar en el clavo
- To cost an arm and a leg: Sacar un ojo de la cara

### Political Idioms Examples:
Tirar la toalla: To throw in the towel (give up)
Example: "Después de los escándalos, el candidato tiró la toalla." (After the scandals, the candidate threw in the towel.)

Dar la vuelta a la tortilla: To turn the tables (reverse a situation)
Example: "El partido en la oposición espera dar la vuelta a la tortilla en las próximas elecciones." (The opposition party hopes to turn the tables in the next election.)

Tener las manos atadas: To have one's hands tied (be unable to act freely)
Example: "El presidente dijo que tiene las manos atadas en cuanto a la reforma fiscal." (The president said that his hands are tied regarding tax reform.)

Echar leña al fuego: To add fuel to the fire (worsen a situation)
Example: "Las declaraciones del ministro solo echaron leña al fuego de la controversia." (The minister's statements only added fuel to the fire of the controversy.)

Estar en la cuerda floja: To be on the ropes (in a precarious situation)
Example: "El partido gobernante está en la cuerda floja después de las protestas." (The ruling party is on the ropes after the protests.)

Lavarse las manos: To wash one's hands of (disclaim responsibility)
Example: "El gobernador se lavó las manos ante la crisis de seguridad." (The governor washed his hands of the security crisis.)

Ser un cero a la izquierda: To be a nobody (have no influence)
Example: "En este gobierno, la opinión del pueblo es un cero a la izquierda." (In this government, the opinion of the people is a nobody.)

Tapar el sol con un dedo: To try to hide something obvious (cover up a problem)
Example: "No se puede tapar el sol con un dedo, la corrupción es evidente." (You can't hide the sun with a finger, corruption is evident.)

### Idioms with a More Mexican Flavor:
Hacerse pato: To play dumb (pretend not to understand)
Example: "El diputado se hizo pato cuando le preguntaron sobre el soborno." (The congressman played dumb when asked about the bribe.)

Echarle la bolita a alguien: To pass the buck (shift responsibility to someone else)
Example: "El presidente le echó la bolita al Congreso por la falta de presupuesto." (The president passed the buck to Congress for the lack of budget.)

Estar como el perro de las dos tortas: To be caught between a rock and a hard place (face a difficult choice)
Example: "El candidato está como el perro de las dos tortas, no sabe si apoyar a los empresarios o a los sindicatos." (The candidate is caught between a rock and a hard place, he doesn't know whether to support the businessmen or the unions.)

No tener pelos en la lengua: To be outspoken (speak frankly)
Example: "El periodista no tiene pelos en la lengua al criticar al gobierno." (The journalist is outspoken in criticizing the government.)

Sacar los trapitos al sol: To air dirty laundry (reveal secrets or scandals)
Example: "La oposición amenaza con sacar los trapitos al sol del partido gobernante." (The opposition threatens to air the dirty laundry of the ruling party.)

### Examples:
- **Example 1**: 
 - **example_input**: The presidential election is one of the most important nights of the year for the United States. The same can be said for The New York Times. The first presidential election covered in The Times was in 1852, a year after the newspaper was established. The news was shared in a column of the eight-page newspaper — then called the New-York Daily Times — the day after the election: Early results indicated that Franklin Pierce, a Democrat, would likely defeat Winfield Scott of the Whig Party. 
 - **example_output**: Las elecciones presidenciales en Estados Unidos constituyen uno de los acontecimientos más importantes del año. Y lo mismo se puede decir de The New York Times. El periódico cubrió su primera elección presidencial en 1852, un año después de su fundación. La noticia se publicó en una columna de su edición de ocho páginas —entonces llamado New-York Daily Times— un día después de la elección: los resultados preliminares indicaban que Franklin Pierce, del partido Demócrata, probablemente derrotaría a Winfield Scott, del partido Whig.

Now, please translate the following text:
"""

model = GenerativeModel(
    gemini_model,
    system_instruction=system_instruction,
)

def gen_ai(text_to_translate: str, model_id: str, result_queue: queue.Queue):
  if model_id == "Claude":
    message=ant_client.messages.create(
        max_tokens=1024,
        system=system_instruction,
        messages=[
            {
                "role": "user",
                "content": f"Give me only the output.\n Input to Translate: \n{text_to_translate}"
            }
        ],
        model=claude_model
    )
    response = json.loads(message.model_dump_json(indent=2))
    result = response["content"][0]["text"]
  else:
    try:
      response = model.generate_content(
          text_to_translate,
      )
      result = response.text
    except Exception as e:
      print(e)
      result = "There was an error with Gemini"
  result_queue.put((model_id, result))

def multithread_func(text_to_translate: str):
  threads = []
  models = ["Claude", "Gemini"]
  for model_id in range(models):
    thread = threading.Thread(target=gen_ai, args=(text_to_translate, model_id))
    threads.append(thread)
    thread.start()

  for thread in threads:
    thread.join()

def main(page: Page):
  output_1 = Text(selectable=True)
  output_2 = Text(selectable=True)
  system_inst: Markdown = Markdown(
      value=system_instruction,
      selectable=True,
      extension_set=MarkdownExtensionSet.GITHUB_WEB,
      soft_line_break=True,
  )

  system_instruction_field: ExpansionTile = ExpansionTile(
      title=Text("System Instructions"),
      controls=[
          ListTile(title=system_inst)
      ]
  )

  output = {}

  def send_instruction(e):
    threads = []
    for model_id in ["Claude", "Gemini"]:
      thread = threading.Thread(target=gen_ai, args=(e.control.value, model_id, result_queue))
      threads.append(thread)
      thread.start()

    for thread in threads:
      thread.join()
    while not result_queue.empty():
      model_id, result = result_queue.get()
      print(f"Result from {model_id}: {result}")
      output[model_id] = result
    output_1.value=output["Gemini"]
    output_2.value=output["Claude"]
    for i in range(2):
      output_field.controls[i].disabled = True
    output_field.update()

  input_field: TextField = TextField(
      label="Input to Translate:",
      multiline=True,
      on_submit=send_instruction,
      shift_enter=True,
  )

  output_field: Row = Row(
      controls=[
          Container(
              disabled=True,
              padding=padding.all(14.0),
              border_radius=14.0,
              border=border.all(1, cupertino_colors.ACTIVE_BLUE),
              height=400,
              expand=1,
              content=Column(
                  alignment=MainAxisAlignment.CENTER,
                  controls=[
                      Text("Gemini", style=TextStyle(weight=FontWeight.BOLD, color=cupertino_colors.ACTIVE_BLUE)),
                      ListView(
                          controls=[
                              output_1
                          ]
                      )
                  ]
              )
          ),
          Container(
              disabled=True,
              padding=padding.all(14.0),
              border_radius=14.0,
              border=border.all(1, cupertino_colors.ACTIVE_BLUE),
              height=400,
              expand=1,
              content=Column(
                  alignment=MainAxisAlignment.CENTER,
                  controls=[
                      Text("Claude", style=TextStyle(weight=FontWeight.BOLD, color=cupertino_colors.ACTIVE_BLUE)),
                      ListView(
                          controls=[
                              output_2
                          ]
                      )
                  ]
              )
          )
      ]
  )

  page.add(
      Column(
          expand=True,
          scroll=ScrollMode.ALWAYS,
          controls=[
              system_instruction_field,
              input_field,
              output_field
          ]
      )
  )
  return None

app(target=main)