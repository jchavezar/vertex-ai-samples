#%%
import json
from flet import *
from agent import Agent

output_schema = {
    "type": "object",
    "properties": {
        "translated_text": {
            "type": "string"
        },
        "justification_and_modifications": {
            "type": "string"
        }
    },
    "required": ["translated_text", "justification_and_modifications"]
}

text_to_translate = """
Israel’s Strike on Iran: A Limited Attack but a Potentially Big Signal
Israel hit a strategic city with carefully measured force, but made the point that it could strike at a center of Iran’s nuclear program.

For more than a decade, Israel has rehearsed, time and again, bombing and missile campaigns that would take out Iran’s nuclear production capability, much of it based around the city of Isfahan and the Natanz nuclear enrichment complex 75 miles to the north.

That is not what Prime Minister Benjamin Netanyahu’s war cabinet chose to do in the predawn hours of Friday, and in interviews, analysts and nuclear experts said the decision was telling.

So was the silence that followed. Israel said almost nothing about the limited strike, which appeared to do little damage in Iran. U.S. officials noted that the Iranian decision to downplay the explosions in Isfahan — and the suggestions by Iranian officials that Israel may not have been responsible — was a clear effort by the Islamic Revolutionary Guards Corps to avoid another round of escalation.

Inside the White House, officials asked the Pentagon, State Department and intelligence agencies to stay quiet about the operation, hoping to ease Iran’s efforts to calm the tensions in the region.

But in interviews, officials quickly added they worried that relations between Israel and Iran were now in a very different place than they had been just a week ago. The taboo against direct strikes on each other’s territory was now gone. If there is another round — a conflict over Iran’s nuclear advances, or another strike by Israel on Iranian military officers — both sides might feel more free to launch directly at the other.

Mr. Netanyahu was under competing pressures: President Biden was urging him to “take the win” after a largely ineffective aerial barrage launched by Iran last week, while hard-liners in Israel were urging him to strike back hard to re-establish deterrence after the first direct effort to strike Israel from Iranian territory in the 45 years since the Iranian revolution.
"""


def llm_pipeline(text_to_translate: str):
  with open("reglas_veracruz.txt", "r") as f:
      rules = f.read()

  translator_agent = Agent(
      model="gemini-1.5-pro-002",
      description=f"""
      You are a linguistic translator expert, your native languages are english and spanish, 
      your parents are from Mexico and United States so you have deep linguistic knowledge about both countries.
      At the same time you work for New York Times as columnist expert to deliver news in spanish for Mexico.
      
      Your main task is to translate from English to Spanish the following article by following the best practices, tone, and gender in the context.
      
      Special Rules:
      - Do literal translation first.
      
      """,
      # file="./documents/nyt_manual.pdf",
      instruction=f"""
      The following document is manual with redaction best practices for Mexico, 
      read it deeply to understand the rules and use it after the translation to tweak 
      the output without losing the original meaning or the semantic context.
    
      If you do not have the document, no worries do your best.
      
      Document with Rules:
      {rules}
      
      Text to Translate:
      {text_to_translate}
      """
  )

  redefine_agent = Agent(
      model="gemini-1.5-pro-002",
      description="""
      You are a columnist for Mexico who works for important news companies like El Universal, Reforma and La Jornada.
      
      Instructions:
      - After receiving a translation (english-spanish) from a linguistic, use your context to **REDFINE** the text based on the tone, style, etc.
      
      Important rules:
      - Pay attention to the gender, dialect and idioms.
      - The following information is not the source of truth, they are examples of important news companies in Mexico.
      - Pay special attention to the gender of the paragraph, read 2-3 paragraphs if needed to achieve it.
      - **1 single output**: if your output contains more than 1 option, merge them and build something unique.
      - Output is the translation after reasoning.
    
      Context (Mexico News Examples):
      ---
      El Universal:
      **Trump premia a su equipo de defensa legal**
      
      De acuerdo con el exmandatario, Blanche 'es un excelente abogado que será un líder crucial, 
      arreglando lo que ha sido un sistema de justicia roto durante demasiado tiempo'
      
      Washington.- Donald Trump, exmandatario y ganador en las elecciones en Estados UNidos, eligió a Todd Blanche, 
      un abogado que dirigió el equipo legal que defendió al republicano en su juicio penal para silenciar a la actriz porno Stormy Daniels, 
      para servir como el segundo funcionario de mayor rango del Departamento de Justicia.
  
      Blanche, un exfiscal federal, ha sido una figura clave en el equipo de defensa de Trump tanto en el caso de Nueva York que terminó en una condena en mayo, 
      como en los casos federales presentados por el fiscal especial del Departamento de Justicia, Jack Smith.
  
      'Todd es un excelente abogado que será un líder crucial en el Departamento de Justicia, arreglando lo que ha sido un sistema de justicia roto durante demasiado tiempo', 
      dijo Trump en un comunicado el jueves al anunciar su elección.
      
      ---
      Reforma:
      'Cortan' con hombres por triunfo de Trump
      
      Tras los resultados de las elecciones del 5 de noviembre, Jada Mevs, una joven de 25 años que vive en D.C. está animando a las mujeres a tomar medidas 
      inscribiéndose en una clase de defensa personal, eliminando aplicaciones de citas, empezando a usar métodos anticonceptivos e invirtiendo en un vibrador.
      
      ---
      La Jornada:
      Mientras Trump promete cerrar fronteras, China abre nuevos caminos en América. ¡Luego que no se quejen! ...
          
      """,
      instruction=f"""
      Spanish Translation to Redefine: {translator_agent.response}
      
      Translation Output:
      <Raw Translation>
      <Explanation and Justification of Changes>
      
      """,
      output_json=True,
      schema=output_schema
  )
  return json.loads(redefine_agent.response)

def main(page: Page):

  response_view: ListView = ListView(
      expand=True,
  )

  explanation_view: ListView = ListView(
      expand=True,
  )

  def send_message(e):
    print("send_message")
    response_view.controls.append(Text("Translating Please Wait...", style=TextStyle(weight=FontWeight.BOLD, color=colors.GREEN)))
    response_view.update()
    re = llm_pipeline(e.control.value)
    print(re)
    response_view.controls[0] = Text(re["translated_text"], selectable=True)
    explanation_view.controls.append(Text(re["justification_and_modifications"], style=TextStyle(weight=FontWeight.BOLD, color=colors.GREEN)))
    explanation_view.update()
    response_view.update()

  main: Column = Column(
      controls=[
          Row(
              controls=[
                  Container(
                      padding=15.0,
                      border=border.all(1, colors.GREY_600),
                      border_radius=14.0,
                      height=700,
                      expand=7,
                      content=response_view
                  ),
                  Container(
                      padding=15.0,
                      border=border.all(1, colors.GREY_600),
                      border_radius=14.0,
                      height=700,
                      expand=3,
                      content=explanation_view
                  )
              ]
          ),
          TextField(
              multiline=True,
              on_submit=send_message,
              shift_enter=True

          ),
      ]
  )
  page.add(
      main
  )

app(target=main)


