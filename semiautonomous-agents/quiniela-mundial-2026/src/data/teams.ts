// Mundial FIFA 2026 - 48 selecciones clasificadas (verificadas al 27 mayo 2026)
// Fuentes: FIFA.com, Wikipedia EN, CBS Sports, Fox Sports
// Badges: TheSportsDB (r2.thesportsdb.com), Banderas: flagcdn.com

export type Confederation = "CONMEBOL" | "CONCACAF" | "UEFA" | "AFC" | "CAF" | "OFC";

export type Team = {
  code: string;          // FIFA 3 letras
  iso2: string;          // ISO 3166-1 alpha-2 (lowercase para flagcdn)
  name: string;          // Nombre oficial en español
  confederation: Confederation;
  group: string;         // A-L
  coach: string;
  stars: string[];       // 1-2 jugadores clave
  stats: string[];       // 1-2 estadísticas
  summary: string;       // Resumen de estilo/expectativa
  ranking: number | null;
  badge: string | null;  // URL del escudo (TheSportsDB)
};

export const TEAMS: Team[] = [
  // Grupo A
  { code: "MEX", iso2: "mx", name: "México", confederation: "CONCACAF", group: "A", coach: "Javier Aguirre", stars: ["Edson Álvarez", "Santiago Giménez"], stats: ["Cuartos de final 1970 y 1986 (como anfitrión)", "Campeón Liga de Naciones CONCACAF 2025"], summary: "Tercer ciclo de Aguirre buscando estabilidad ofensiva. Como anfitrión apunta a igualar los cuartos históricos.", ranking: 15, badge: "https://r2.thesportsdb.com/images/media/team/badge/3rmosi1748525208.png" },
  { code: "KOR", iso2: "kr", name: "Corea del Sur", confederation: "AFC", group: "A", coach: "Hong Myung-bo", stars: ["Son Heung-min", "Lee Kang-in"], stats: ["4to lugar en 2002 como anfitrión", "Primera asiática en llegar a semifinales"], summary: "Juego vertical anclado en la velocidad de Son y la creatividad de Lee. Pelea por la zona de octavos.", ranking: 23, badge: "https://r2.thesportsdb.com/images/media/team/badge/uqxrtt1448811346.png" },
  { code: "CZE", iso2: "cz", name: "República Checa", confederation: "UEFA", group: "A", coach: "Miroslav Koubek", stars: ["Ladislav Krejčí", "Patrik Schick"], stats: ["Segunda participación como Chequia", "Clasificó vía repechaje UEFA"], summary: "Bloque defensivo y juego directo con Schick como referencia ofensiva. Pelea por el segundo lugar.", ranking: null, badge: null },
  { code: "RSA", iso2: "za", name: "Sudáfrica", confederation: "CAF", group: "A", coach: "Hugo Broos", stars: ["Ronwen Williams", "Themba Zwane"], stats: ["Cuarta participación mundialista", "Tercer lugar Copa Africana 2023"], summary: "Juego asociado y arquero estelar en Williams. Llega en su mejor momento desde 2010.", ranking: null, badge: null },

  // Grupo B
  { code: "CAN", iso2: "ca", name: "Canadá", confederation: "CONCACAF", group: "B", coach: "Jesse Marsch", stars: ["Alphonso Davies", "Jonathan David"], stats: ["Tercera participación mundialista", "Anfitrión automático"], summary: "Presión alta a la Marsch con Davies por banda y David como referencia ofensiva. Como local apunta a su primera victoria.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/yvsq2g1448811325.png" },
  { code: "SUI", iso2: "ch", name: "Suiza", confederation: "UEFA", group: "B", coach: "Murat Yakin", stars: ["Granit Xhaka", "Manuel Akanji"], stats: ["Cuartos (1934, 1938, 1954)", "Cuartos Eurocopa 2024"], summary: "Bloque medio compacto con Xhaka conduciendo. Equipo serio capaz de complicar a cualquiera.", ranking: 19, badge: null },
  { code: "QAT", iso2: "qa", name: "Catar", confederation: "AFC", group: "B", coach: "Julen Lopetegui", stars: ["Almoez Ali", "Akram Afif"], stats: ["Segunda participación (debut 2022)", "Bicampeón Copa Asiática (2019, 2023)"], summary: "Primera clasificación vía eliminatorias con Lopetegui. Genera identidad propia más allá del estatus de anfitrión previo.", ranking: null, badge: null },
  { code: "BIH", iso2: "ba", name: "Bosnia y Herzegovina", confederation: "UEFA", group: "B", coach: "Sergej Barbarez", stars: ["Edin Džeko", "Sead Kolašinac"], stats: ["Segunda participación (debut 2014)", "Eliminaron a Italia en playoffs"], summary: "Equipo combativo apoyado en la jerarquía ofensiva de Džeko. Llega con la confianza de haber tumbado a Italia.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/30vurc1448811335.png" },

  // Grupo C
  { code: "BRA", iso2: "br", name: "Brasil", confederation: "CONMEBOL", group: "C", coach: "Carlo Ancelotti", stars: ["Vinícius Jr.", "Rodrygo"], stats: ["Pentacampeón (1958, 1962, 1970, 1994, 2002)", "Máximo ganador de Copas del Mundo"], summary: "Por primera vez con un DT extranjero (Ancelotti) buscando recuperar identidad ofensiva. Vinícius es el referente.", ranking: 6, badge: "https://r2.thesportsdb.com/images/media/team/badge/qsv4yt1455368559.png" },
  { code: "MAR", iso2: "ma", name: "Marruecos", confederation: "CAF", group: "C", coach: "Mohamed Ouahbi", stars: ["Achraf Hakimi", "Yassine Bounou"], stats: ["4to lugar Qatar 2022 (mejor africana en historia)", "Récord mundial 19 victorias consecutivas en 2025"], summary: "Bloque defensivo elite con Bounou y Hakimi como referentes. Candidata real a repetir semifinal.", ranking: 8, badge: "https://r2.thesportsdb.com/images/media/team/badge/uitixv1654783672.png" },
  { code: "HAI", iso2: "ht", name: "Haití", confederation: "CONCACAF", group: "C", coach: "Sébastien Migné", stars: ["Duckens Nazon", "Johny Plácide"], stats: ["Regresa tras 52 años (1974)", "Única nación caribeña en jugar un Mundial"], summary: "Retorno histórico con un equipo guerrero y emocional. Su objetivo realista es competir y dejar puntos.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/wptqxv1448811338.png" },
  { code: "SCO", iso2: "gb-sct", name: "Escocia", confederation: "UEFA", group: "C", coach: "Steve Clarke", stars: ["Andy Robertson", "Scott McTominay"], stats: ["Regresa tras 28 años (1998)", "Nunca ha superado fase de grupos"], summary: "Bloque sólido y juego intenso con Robertson como capitán. Por fin tiene plantel para soportar a un grupo de elite.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/cmt2u41633976657.png" },

  // Grupo D
  { code: "USA", iso2: "us", name: "Estados Unidos", confederation: "CONCACAF", group: "D", coach: "Mauricio Pochettino", stars: ["Christian Pulisic", "Weston McKennie"], stats: ["Tercer lugar 1930", "Anfitrión del torneo (11 sedes)"], summary: "Pochettino busca dar identidad ofensiva a la generación dorada de Pulisic. Como local apunta a mejorar octavos 2022.", ranking: 16, badge: "https://r2.thesportsdb.com/images/media/team/badge/4sjnww1735068494.png" },
  { code: "PAR", iso2: "py", name: "Paraguay", confederation: "CONMEBOL", group: "D", coach: "Gustavo Alfaro", stars: ["Miguel Almirón", "Gustavo Gómez"], stats: ["Cuartos de final 2010", "Décima participación, primera desde 2010"], summary: "Defensa sólida, transiciones largas y mucha garra a la Alfaro. Vuelve al Mundial tras 16 años.", ranking: 40, badge: "https://r2.thesportsdb.com/images/media/team/badge/uqsyru1448811347.png" },
  { code: "AUS", iso2: "au", name: "Australia", confederation: "AFC", group: "D", coach: "Tony Popovic", stars: ["Mathew Ryan", "Harry Souttar"], stats: ["Sexta participación consecutiva", "Octavos en 2006 y 2022"], summary: "Bloque defensivo sólido y juego directo apoyado en transiciones largas. Buscará repetir octavos.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/wxupwt1448811322.png" },
  { code: "TUR", iso2: "tr", name: "Turquía", confederation: "UEFA", group: "D", coach: "Vincenzo Montella", stars: ["Arda Güler", "Hakan Çalhanoğlu"], stats: ["Tercer lugar 2002", "Regresa tras 24 años"], summary: "Generación joven encabezada por Güler con creatividad y verticalidad. Una de las sorpresas más mediáticas.", ranking: null, badge: null },

  // Grupo E
  { code: "GER", iso2: "de", name: "Alemania", confederation: "UEFA", group: "E", coach: "Julian Nagelsmann", stars: ["Florian Wirtz", "Jamal Musiala"], stats: ["Tetracampeón (1954, 1974, 1990, 2014)", "Cuatro veces subcampeón"], summary: "Generación brillante con Wirtz y Musiala, dirigida por Nagelsmann. Vuelve a posicionarse entre las grandes candidatas.", ranking: 10, badge: null },
  { code: "ECU", iso2: "ec", name: "Ecuador", confederation: "CONMEBOL", group: "E", coach: "Sebastián Beccacece", stars: ["Moisés Caicedo", "Enner Valencia"], stats: ["Quinta participación", "Octavos en 2006"], summary: "Equipo físico con Caicedo como dueño del medio. Aspira a romper su techo de octavos en un grupo accesible.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/3xy8531574094895.png" },
  { code: "CUW", iso2: "cw", name: "Curazao", confederation: "CONCACAF", group: "E", coach: "Dick Advocaat", stars: ["Leandro Bacuna", "Juninho Bacuna"], stats: ["Primera participación en historia", "Nación más pequeña por población en clasificar"], summary: "Debutante absoluto con un DT veterano. Bloque bajo y contragolpe serán su carta.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/2hh38g1735067962.png" },
  { code: "CIV", iso2: "ci", name: "Costa de Marfil", confederation: "CAF", group: "E", coach: "Emerse Faé", stars: ["Franck Kessié", "Sébastien Haller"], stats: ["Campeón Copa Africana 2023", "Cuarta participación mundialista"], summary: "Llega como tricampeón africano con una generación física y técnica. Examen serio para Alemania y Ecuador.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/0eu1jm1734977094.png" },

  // Grupo F
  { code: "NED", iso2: "nl", name: "Países Bajos", confederation: "UEFA", group: "F", coach: "Ronald Koeman", stars: ["Virgil van Dijk", "Cody Gakpo"], stats: ["Subcampeón 3 veces (1974, 1978, 2010)", "Nunca ha sido campeón"], summary: "Bloque alto con salida desde Van Dijk y velocidad de Gakpo. Candidata europea a semifinales.", ranking: 7, badge: "https://r2.thesportsdb.com/images/media/team/badge/zpwzpu1448811340.png" },
  { code: "JPN", iso2: "jp", name: "Japón", confederation: "AFC", group: "F", coach: "Hajime Moriyasu", stars: ["Takefusa Kubo", "Wataru Endo"], stats: ["Octavos en 2002, 2010, 2018, 2022", "Ganó su grupo en Qatar dejando fuera a Alemania"], summary: "Juego asociado de toques cortos y presión alta coordinada. Aspira a romper el techo de octavos.", ranking: 18, badge: "https://r2.thesportsdb.com/images/media/team/badge/uxxupu1448811420.png" },
  { code: "SWE", iso2: "se", name: "Suecia", confederation: "UEFA", group: "F", coach: "Graham Potter", stars: ["Alexander Isak", "Viktor Gyökeres"], stats: ["Subcampeón 1958", "Clasificó vía repechaje 3-2 a Polonia"], summary: "Doble nueve de elite (Isak + Gyökeres) y Potter ordenando el bloque. Candidata real a octavos.", ranking: null, badge: null },
  { code: "TUN", iso2: "tn", name: "Túnez", confederation: "CAF", group: "F", coach: "Sabri Lamouchi", stars: ["Ellyes Skhiri", "Hannibal Mejbri"], stats: ["Séptima participación, nunca pasó de grupos", "Clasificó sin recibir goles (récord, oct 2025)"], summary: "Defensa hermética, ataque limitado. Buscará romper su maldición de fase de grupos.", ranking: null, badge: null },

  // Grupo G
  { code: "BEL", iso2: "be", name: "Bélgica", confederation: "UEFA", group: "G", coach: "Rudi Garcia", stars: ["Kevin De Bruyne", "Romelu Lukaku"], stats: ["Tercer lugar 2018", "Única en ser #1 FIFA sin trofeo mayor"], summary: "Generación dorada en fase final con De Bruyne todavía como cerebro. Aspirante a cuartos sin el favoritismo previo.", ranking: 9, badge: "https://r2.thesportsdb.com/images/media/team/badge/30tnh51612882324.png" },
  { code: "EGY", iso2: "eg", name: "Egipto", confederation: "CAF", group: "G", coach: "Hossam Hassan", stars: ["Mohamed Salah", "Omar Marmoush"], stats: ["Heptacampeón Copa Africana (récord)", "Cuarta participación mundialista"], summary: "El Mundial dependerá del estado de Salah, su referencia absoluta. Juego pragmático buscando transiciones.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/wsxuyu1448811354.png" },
  { code: "IRN", iso2: "ir", name: "Irán", confederation: "AFC", group: "G", coach: "Amir Ghalenoei", stars: ["Mehdi Taremi", "Sardar Azmoun"], stats: ["Séptima participación", "Nunca ha superado fase de grupos"], summary: "Equipo físico y disciplinado con dos delanteros de nivel europeo. Pelea con Egipto y NZ por segundo lugar.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/uxxutq1448811422.png" },
  { code: "NZL", iso2: "nz", name: "Nueva Zelanda", confederation: "OFC", group: "G", coach: "Darren Bazeley", stars: ["Chris Wood", "Marko Stamenic"], stats: ["Tercera participación (1982, 2010, 2026)", "Única invicta en Sudáfrica 2010"], summary: "Equipo físico y directo apoyado en la potencia de Wood. Buscará replicar la imagen de Sudáfrica 2010.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/uwsvyt1448811323.png" },

  // Grupo H
  { code: "ESP", iso2: "es", name: "España", confederation: "UEFA", group: "H", coach: "Luis de la Fuente", stars: ["Lamine Yamal", "Rodri"], stats: ["Campeón del mundo 2010", "Campeón Eurocopa 2024 (7 de 7 ganados)"], summary: "Mejor seleccion europea del ciclo con Yamal como estrella generacional. Principal candidata europea al título.", ranking: 2, badge: "https://r2.thesportsdb.com/images/media/team/badge/yrwspu1448811352.png" },
  { code: "URU", iso2: "uy", name: "Uruguay", confederation: "CONMEBOL", group: "H", coach: "Marcelo Bielsa", stars: ["Federico Valverde", "Darwin Núñez"], stats: ["Bicampeón (1930, 1950)", "4 estrellas con olímpicos reconocidos"], summary: "Bielsa imprime presión alta y juego vertical con una generación joven y poderosa. Candidata real a semifinales.", ranking: 17, badge: null },
  { code: "KSA", iso2: "sa", name: "Arabia Saudita", confederation: "AFC", group: "H", coach: "Georgios Donis", stars: ["Salem Al-Dawsari", "Salman Al-Faraj"], stats: ["Octavos 1994", "Séptima participación mundialista"], summary: "Equipo ordenado defensivamente con Al-Dawsari como gran arma. Tras vencer a Argentina en 2022, busca otra sorpresa.", ranking: null, badge: null },
  { code: "CPV", iso2: "cv", name: "Cabo Verde", confederation: "CAF", group: "H", coach: "Pedro 'Bubista' Leitão Brito", stars: ["Ryan Mendes", "Garry Rodrigues"], stats: ["Primera participación en historia", "País más pequeño por superficie clasificado"], summary: "Debut histórico de una isla con 525 mil habitantes y juego ordenado de transición. Equipo sorpresa sentimental.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/qttvxv1448811337.png" },

  // Grupo I
  { code: "FRA", iso2: "fr", name: "Francia", confederation: "UEFA", group: "I", coach: "Didier Deschamps", stars: ["Kylian Mbappé", "Aurélien Tchouaméni"], stats: ["Campeón 1998 y 2018", "Subcampeón 2022, último torneo de Deschamps"], summary: "Plantilla profunda en todas las líneas con Mbappé en su pico físico. Favorita junto a Argentina y España al título.", ranking: 1, badge: "https://r2.thesportsdb.com/images/media/team/badge/dipv811733416902.png" },
  { code: "SEN", iso2: "sn", name: "Senegal", confederation: "CAF", group: "I", coach: "Pape Thiaw", stars: ["Sadio Mané", "Kalidou Koulibaly"], stats: ["Cuartos de final 2002", "Campeón Copa Africana 2021"], summary: "Equipo físico y veloz con Mané como referencia. Una de las africanas con plantilla más equilibrada del torneo.", ranking: 14, badge: null },
  { code: "NOR", iso2: "no", name: "Noruega", confederation: "UEFA", group: "I", coach: "Ståle Solbakken", stars: ["Erling Haaland", "Martin Ødegaard"], stats: ["Regresa tras 28 años (1998)", "Haaland: máximo goleador histórico (55 goles)"], summary: "La dupla Haaland-Ødegaard la hace una de las grandes incógnitas. Si compiten en defensa, candidata a cuartos.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/sttwru1448811330.png" },
  { code: "IRQ", iso2: "iq", name: "Irak", confederation: "AFC", group: "I", coach: "Graham Arnold", stars: ["Aymen Hussein", "Jalal Hassan"], stats: ["Segunda participación (debut 1986)", "Venció a Bolivia en repechaje"], summary: "Regreso a un Mundial tras 40 años con Arnold (ex-Australia) al mando. Bloque competitivo en defensa.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/0vlbpf1737495321.png" },

  // Grupo J
  { code: "ARG", iso2: "ar", name: "Argentina", confederation: "CONMEBOL", group: "J", coach: "Lionel Scaloni", stars: ["Lionel Messi", "Lautaro Martínez"], stats: ["Campeón 3 veces (1978, 1986, 2022)", "Vigente campeón Mundo y Copa América 2024"], summary: "Posesión vertical con presión alta y un Messi orquestador en su probable último Mundial. Llega como favorita firme.", ranking: 3, badge: "https://r2.thesportsdb.com/images/media/team/badge/3zplhu1726167477.png" },
  { code: "ALG", iso2: "dz", name: "Argelia", confederation: "CAF", group: "J", coach: "Vladimir Petković", stars: ["Riyad Mahrez", "Ismael Bennacer"], stats: ["Octavos de final 2014", "Regresa tras ausencias 2018 y 2022"], summary: "Equipo técnico apoyado en la creatividad de Mahrez y la salida limpia de Bennacer. Aspira a repetir el hito de 2014.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/rrwpry1455460218.png" },
  { code: "AUT", iso2: "at", name: "Austria", confederation: "UEFA", group: "J", coach: "Ralf Rangnick", stars: ["David Alaba", "Marko Arnautović"], stats: ["Regresa tras 28 años", "Tercer lugar 1954"], summary: "Estilo de gegenpressing inculcado por Rangnick con presión ultra agresiva. Una de las sorpresas potenciales.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/m70qkk1722593753.png" },
  { code: "JOR", iso2: "jo", name: "Jordania", confederation: "AFC", group: "J", coach: "Jamal Sellami", stars: ["Ali Olwan", "Ihsan Haddad"], stats: ["Primera participación en historia", "Subcampeón Copa Asiática 2023"], summary: "Debutante absoluto que compite con orden táctico y buen pie a balón parado. Reto enorme: debuta vs Argentina.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/qfrigw1735068083.png" },

  // Grupo K
  { code: "POR", iso2: "pt", name: "Portugal", confederation: "UEFA", group: "K", coach: "Roberto Martínez", stars: ["Cristiano Ronaldo", "Bruno Fernandes"], stats: ["Tercer lugar 1966", "Campeón UEFA Nations League 2025"], summary: "Último baile de Cristiano con una plantilla profundísima. Aspira a su primera final mundialista.", ranking: 5, badge: null },
  { code: "COL", iso2: "co", name: "Colombia", confederation: "CONMEBOL", group: "K", coach: "Néstor Lorenzo", stars: ["James Rodríguez", "Luis Díaz"], stats: ["Cuartos de final 2014", "Subcampeón Copa América 2024"], summary: "Posesión fluida con James como conductor y Díaz como ejecutor por izquierda. Candidata sudamericana a cuartos.", ranking: 13, badge: "https://r2.thesportsdb.com/images/media/team/badge/swyyru1448811328.png" },
  { code: "COD", iso2: "cd", name: "RD del Congo", confederation: "CAF", group: "K", coach: "Sébastien Desabre", stars: ["Chancel Mbemba", "Yoane Wissa"], stats: ["Segunda participación (1974 como Zaire)", "Clasificó venciendo a Jamaica en repechaje"], summary: "Equipo físico y veloz con jugadores en ligas europeas. Reto enorme en un grupo con Portugal y Colombia.", ranking: null, badge: null },
  { code: "UZB", iso2: "uz", name: "Uzbekistán", confederation: "AFC", group: "K", coach: "Fabio Cannavaro", stars: ["Eldor Shomurodov", "Abbosbek Fayzullaev"], stats: ["Primera participación en historia", "Primera nación centroasiática en clasificar"], summary: "Debut histórico con Cannavaro al mando y un equipo técnico bien armado. Será incómodo para Portugal y Colombia.", ranking: null, badge: null },

  // Grupo L
  { code: "ENG", iso2: "gb-eng", name: "Inglaterra", confederation: "UEFA", group: "L", coach: "Thomas Tuchel", stars: ["Harry Kane", "Jude Bellingham"], stats: ["Campeón 1966", "Primera europea en clasificar (6 de 6)"], summary: "Tuchel le da estructura táctica a una plantilla de elite con Bellingham y Kane. Candidata seria al título.", ranking: 4, badge: "https://r2.thesportsdb.com/images/media/team/badge/eatv2j1571719005.png" },
  { code: "CRO", iso2: "hr", name: "Croacia", confederation: "UEFA", group: "L", coach: "Zlatko Dalić", stars: ["Luka Modrić", "Joško Gvardiol"], stats: ["Subcampeón 2018 y tercero 2022", "Modrić, jugador con más partidos en historia croata (196)"], summary: "Mediocampo dominante alrededor de Modrić, todavía maestro del ritmo. Candidata a cuartos.", ranking: 11, badge: "https://r2.thesportsdb.com/images/media/team/badge/2lj3y31591375886.png" },
  { code: "GHA", iso2: "gh", name: "Ghana", confederation: "CAF", group: "L", coach: "Carlos Queiroz", stars: ["Mohammed Kudus", "Jordan Ayew"], stats: ["Cuartos de final 2010", "Quinta participación mundialista"], summary: "Recambio generacional alrededor de Kudus, su gran talento ofensivo. Queiroz llegó en abril 2026 para ordenar.", ranking: null, badge: "https://r2.thesportsdb.com/images/media/team/badge/uxsqsw1448811427.png" },
  { code: "PAN", iso2: "pa", name: "Panamá", confederation: "CONCACAF", group: "L", coach: "Thomas Christiansen", stars: ["Aníbal Godoy", "Ismael Díaz"], stats: ["Segunda participación (debut 2018)", "Subcampeón Liga de Naciones CONCACAF 2025"], summary: "Equipo experimentado bajo Christiansen, con disciplina defensiva. Reto duro en el Grupo L.", ranking: null, badge: null },
];

export const TEAMS_BY_CODE: Record<string, Team> = Object.fromEntries(
  TEAMS.map(t => [t.code, t])
);

export function getTeam(code: string): Team | undefined {
  return TEAMS_BY_CODE[code];
}

const FLAGCDN_WIDTHS = [20, 40, 80, 160, 320, 640, 1280, 2560];

export function flagUrl(iso2: string, width = 80): string {
  const w = FLAGCDN_WIDTHS.find(v => v >= width) ?? 640;
  return `https://flagcdn.com/w${w}/${iso2.toLowerCase()}.png`;
}

export function flagSvg(iso2: string): string {
  return `https://flagcdn.com/${iso2.toLowerCase()}.svg`;
}

export const CONFEDERATION_COLORS: Record<Confederation, string> = {
  CONMEBOL:  "#FFD700", // dorado
  UEFA:      "#3B82F6", // azul
  CONCACAF:  "#10B981", // verde esmeralda
  AFC:       "#EF4444", // rojo
  CAF:       "#F59E0B", // ámbar
  OFC:       "#06B6D4", // cian
};
