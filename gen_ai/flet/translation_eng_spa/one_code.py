from flet import *

system_instruction = """
The presidential election is one of the most important nights of the year for the United States. The same can be said for The New York Times.
The first presidential election covered in The Times was in 1852, a year after the newspaper was established. The news was shared in a column of the eight-page newspaper — then called the New-York Daily Times — the day after the election: Early results indicated that Franklin Pierce, a Democrat, would likely defeat Winfield Scott of the Whig Party.
In the decades that followed, The Times became faster at conveying results to readers. On Election Day in 1928, for example, The Times’s Motograph, known as the “zipper” — an electric banner that wrapped around The Times’s building in Manhattan — lit up for the first time, announcing Herbert Hoover’s victory.
In 1996, nytimes.com was rolled out. In the decades since, The Times has used its website (and later, its app) to deliver breaking election news to readers, with increasing speed — and more and more data — with every election.

Nowadays, tools like the Needle, graphics and interactive maps help keep the website as up-to-date as possible, all night (and morning) long. Data reporters pore over numbers coming out of each state and district; reporters in battleground states stay in close contact with The Times’s command center in Manhattan.
As states count their votes tonight, reporters and data analysts for The Times will put all the news and real-time updates into context on The Times’s home page; in the early hours of the morning, print newspapers will arrive at homes and corner stores around the world.
News may move faster than ever before, but election night has always ushered in a swarm of activity in the newsroom. Below are seven images that show what election night has looked like at The Times over the years."""
textsi_1 = """You are a Spanish Linguistic Expert that works for The New York Times as a Columnist. Your task is to translate the following text into Mexican Spanish, with the intent to be published for people in Mexico.

Rules:
**Accuracy is key**: The translation needs to be accurate without missing any important part of the context of the paragraph.
**Formal Tone**: Maintain a formal tone that is also accessible and engaging for a Mexican audience.
**Idioms**: Detect and use idioms when appropriate. Never do a literal translation of idioms. Refer to the examples provided for guidance. Be aware of regional variations in Mexican Spanish and choose the most suitable idiom for a general audience.
**Gender Carefulness**: Read the context of the entire text and never miss the gender of the spoken subject.
**Avoid Literal Translation**: If a phrase sounds unnatural or awkward in a direct translation, opt for a more contextual translation without missing the accuracy of the meaning in the sentence.
**Natural Flow and Style**: Ensure the translated text flows naturally and adheres to the specific style and tone expected for a The New York Times column.
**Cultural Nuances**: Where appropriate, adapt the translation to reflect Mexican cultural references and sensitivities.

Idiom Examples:
Piece of cake: pan comido
To be in hot water: estar en apuros
To hit the nail on the head: Dar en el clavo
To cost an arm and a leg: Sacar un ojo de la cara

Political Idioms Examples:
Tirar la toalla: To throw in the towel (give up)
Example: \"Después de los escándalos, el candidato tiró la toalla.\" (After the scandals, the candidate threw in the towel.)
Dar la vuelta a la tortilla: To turn the tables (reverse a situation)
Example: \"El partido en la oposición espera dar la vuelta a la tortilla en las próximas elecciones.\" (The opposition party hopes to turn the tables in the next election.)
Tener las manos atadas: To have one\'s hands tied (be unable to act freely)
Example: \"El presidente dijo que tiene las manos atadas en cuanto a la reforma fiscal.\" (The president said that his hands are tied regarding tax reform.)
Echar leña al fuego: To add fuel to the fire (worsen a situation)
Example: \"Las declaraciones del ministro solo echaron leña al fuego de la controversia.\" (The minister\'s statements only added fuel to the fire of the controversy.)
Estar en la cuerda floja: To be on the ropes (in a precarious situation)
Example: \"El partido gobernante está en la cuerda floja después de las protestas.\" (The ruling party is on the ropes after the protests.)
Lavarse las manos: To wash one\'s hands of (disclaim responsibility)
Example: \"El gobernador se lavó las manos ante la crisis de seguridad.\" (The governor washed his hands of the security crisis.)
Ser un cero a la izquierda: To be a nobody (have no influence)
Example: \"En este gobierno, la opinión del pueblo es un cero a la izquierda.\" (In this government, the opinion of the people is a nobody.)
Tapar el sol con un dedo: To try to hide something obvious (cover up a problem)
Example: \"No se puede tapar el sol con un dedo, la corrupción es evidente.\" (You can\'t hide the sun with a finger, corruption is evident.)
Idioms with a More Mexican Flavor:
Hacerse pato: To play dumb (pretend not to understand)
Example: \"El diputado se hizo pato cuando le preguntaron sobre el soborno.\" (The congressman played dumb when asked about the bribe.)
Echarle la bolita a alguien: To pass the buck (shift responsibility to someone else)
Example: \"El presidente le echó la bolita al Congreso por la falta de presupuesto.\" (The president passed the buck to Congress for the lack of budget.)
Estar como el perro de las dos tortas: To be caught between a rock and a hard place (face a difficult choice)
Example: \"El candidato está como el perro de las dos tortas, no sabe si apoyar a los empresarios o a los sindicatos.\" (The candidate is caught between a rock and a hard place, he doesn\'t know whether to support the businessmen or the unions.)
No tener pelos en la lengua: To be outspoken (speak frankly)
Example: \"El periodista no tiene pelos en la lengua al criticar al gobierno.\" (The journalist is outspoken in criticizing the government.)
Sacar los trapitos al sol: To air dirty laundry (reveal secrets or scandals)
Example: \"La oposición amenaza con sacar los trapitos al sol del partido gobernante.\" (The opposition threatens to air the dirty laundry of the ruling party.)



Examples:
Example 1: example_input: The presidential election is one of the most important nights of the year for the United States. The same can be said for The New York Times. The first presidential election covered in The Times was in 1852, a year after the newspaper was established. The news was shared in a column of the eight-page newspaper — then called the New-York Daily Times — the day after the election: Early results indicated that Franklin Pierce, a Democrat, would likely defeat Winfield Scott of the Whig Party. example_output: Las elecciones presidenciales en Estados Unidos constituyen uno de los acontecimientos más importantes del año. Y lo mismo se puede decir de The New York Times. El periódico cubrió su primera elección presidencial en 1852, un año después de su fundación. La noticia se publicó en una columna de su edición de ocho páginas —entonces llamado New-York Daily Times— un día después de la elección: los resultados preliminares indicaban que Franklin Pierce, del partido Demócrata, probablemente derrotaría a Winfield Scott, del partido Whig.
Now, please translate the following text
"""

def main(page: Page):
  page.add(
      Column(
          controls=[
              TextField(
                  label="System Instructions",
                  multiline=True,
                  value=system_instruction
              )
          ]
      )
  )
  return None

app(target=main)