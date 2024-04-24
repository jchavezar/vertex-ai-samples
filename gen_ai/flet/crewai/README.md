## CrewAI 

CrewAI is a platform to run AI Agents for frameworks that are complex,
the platform orchestrates role-playing, autonomouns AI agents, by fostering
collaboraite intelligence.

## Architecture

![Architecture](diagram.png)


## Front End Presentation

![front end](./crewai.png)

## Prework

Install all the python packages required to run this script:

```bash
pip install -r requirements.txt
```

Use the [getting started guide](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search) to create a RAG with Vertex Search.

## Components Used
- [Vertex Gemini 1.0](https://cloud.google.com/vertex-ai?hl=en)
- [Vertex Search](https://cloud.google.com/enterprise-search?hl=en)
- [CrewAI](https://www.crewai.com/)
- [Langchain (for tooling)](https://www.langchain.com/)
- [Flet (Python Front End Framework)](https://flet.dev/)

## Using the script

```bash
flet run crewai.py
```

## Results

```markdown
Mexico boasts a rich and vibrant culture that has evolved over centuries, blending indigenous traditions with European influences. It is a land renowned for its passionate people, lively festivals, delicious cuisine, and unique artistic expressions. This report offers a glimpse into the diverse aspects of Mexican culture, highlighting its key features, historical influences, and recent developments.

**Core Values and Customs:**

* **Family-Centric:** Family forms the bedrock of Mexican society, playing a pivotal role in daily life. Strong bonds are maintained between generations, with extended families often living in close proximity. Respect for elders is paramount, and children are raised with a strong sense of responsibility towards their families.
* **Collectivism:** Mexicans tend to prioritize the needs of the collective over individual desires. This is evident in their communal spirit, emphasis on social harmony, and strong sense of community.
* **Respect and Hospitality:** Mexicans are known for their warmth, hospitality, and genuine respect for others. They often go out of their way to make visitors feel welcome and comfortable, showcasing their generous spirit.
* **Celebration of Life:** Mexicans embrace a joyful approach to life, celebrating every occasion with gusto. From vibrant fiestas to lively gatherings, music, dance, and laughter permeate their daily routines.

**Historical Influences:**

* **Indigenous Heritage:** Mexico's indigenous roots are deeply embedded in its culture. From the ancient Aztecs and Mayans to numerous other groups, their traditions, beliefs, and languages continue to influence various aspects of Mexican life, including art, music, cuisine, and spirituality.
* **Spanish Colonization:** The Spanish conquest in the 16th century left an undeniable mark on Mexican culture. Spanish language, religion, and architectural styles became integrated into the existing indigenous practices, creating a unique blend.
* **Global Influences:** Over time, Mexico has absorbed elements from other cultures, including African and Asian influences, enriching its cultural tapestry further.

**Recent Developments:**

* **Modernization:** Mexico has witnessed significant modernization in recent years, particularly in urban areas. This has led to changes in lifestyle, technology adoption, and increased exposure to global trends. However, traditional values and customs continue to hold strong alongside these advancements.
* **Cultural Preservation:** There is a growing awareness and appreciation for preserving Mexican cultural heritage. Efforts are underway to safeguard traditional art forms, languages, and customs, ensuring their continuity for future generations.
* **Diaspora Influence:** The Mexican diaspora has played a crucial role in disseminating aspects of Mexican culture worldwide. From traditional cuisine and music to artistic expressions and cultural events, Mexican communities abroad contribute to the global understanding and appreciation of their rich heritage.

**Conclusion:**

Mexican culture is a dynamic and multifaceted entity, constantly evolving while preserving its core values. Its vibrant traditions, historical influences, and recent developments create a unique and fascinating cultural landscape. As Mexico continues to navigate the modern world, its cultural heritage remains a vital source of identity, pride, and inspiration for its people.

**Additional Findings:**

* Recent research suggests that cultural factors like collectivism and family orientation contribute to Mexicans' higher levels of subjective well-being.
* The Mexican government has implemented initiatives to promote cultural diversity and inclusion, recognizing the value of its rich heritage.
* Mexican artists, musicians, and filmmakers are increasingly gaining international recognition, showcasing the country's vibrant creative scene.

This report provides a starting point for exploring the vast and captivating world of Mexican culture. With its rich history, diverse customs, and dynamic expressions, Mexico continues to captivate and inspire audiences worldwide.
```