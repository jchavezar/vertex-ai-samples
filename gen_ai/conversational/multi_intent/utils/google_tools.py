import vertexai
from vertexai.language_models import ChatModel


class llm:
    def __init__(self, 
                 model: str = "chat-bison@001", 
                 location: str ="us-central1"):
        
        self.parameters = {
            "candidate_count": 1,
            "max_output_tokens": 1024,
            "temperature": 0,
            "top_p": 0.6,
            "top_k": 5
        }
        
        self.prompts = {
            "default_intent":  """
            You are a chatbot assistant and your name chatty, you are a very funny and talented bot.
            
            provided_context:
                allowed_topics:
                    - Account support provides an interface to query assets based on user accounts, like billing, profiles, addresses, your name etc.
                    - Product_prices, Offers support anything related to product description and pricing.
                    - Marketing_campaigns,Interface to query things related to marketing.
            
            explicit_instructions:
            - You can only be asked by your name or jokes, but you can not answer any additional questions.
            - If the human ask you for questions not related to how you feel, greetings or jokes, just tell him you do not know the answer.
            - Do not give me any information about anything that are not mentioned in the provided_context."
            
            If your answer is "I do not know it" you can tell the things you can answer related to the provided_context.
            
            chat_history: 
            """,
            
            "product_prices": """
            You are a chatbot assistant and your name is adaline, you are an expert in Analytics on Products provides an interface to query about product information.
            
            Context:
            1. Mercedes benz price $65,000, they are in colors gray, blue and black.
            2. Honda price $50,0000 they are in colors black and white.
            """,
            
            "marketing_campaigns":  """
            You are a chatbot assistant and your name is morphy, you are an expert in building campaigns.
            Create a campaign given the following best practices:
            
            - Start with strong idea.
            - Try to engage people by telling a story.
            - Try to be funny.
            
            chat_history:
            """,
            "account_support":  """
            You are a chatbot assistant and your name is accounty, you are an expert in profile events.
            You can be asked for anythin related to your account.
            
            chat_history:
            """
            }
        
        vertexai.init(project="jesusarguelles-sandbox", location=location)
        
        self.chat_model = ChatModel.from_pretrained(model)

    
    def chat_intent_detection(self, prompt):
        self.query = prompt
        chat = self.chat_model.start_chat(
            context="""Your only task is to detect the intent of the prompt, nothing else, the supported issue type helps to identify the intent.
        
        intents_of_the_prompt:            
        - intent: account_support, description: Account support provides an interface to query assets based on user accounts, like billing, profiles, addresses, etc.
        - intent: product_prices, description: Offers support anything related to product description and pricing.
        - intent: marketing_campaigns, description: Interface to query things related to marketing.
        - intent: default_intent, anything else..
        
        instructions:
        1. If user input is about account support return account_support.
        2. If user input is about product prices return product_prices.
        3. If user input is about marketing or campaigns return marketing_campaigns.
        5. If user input is everything else not related to point from 1-3, e.g. greetings, take input from user and return default_intent.

        Your output is just the intent, do try to answer any question.

        Response only one (do not answer any other sentence): e.g.: <default_intent> or <account_support> or <product_prices> or <marketing_campaigns>
        """,
        )
        
        return str(chat.send_message(prompt, **self.parameters).text.strip())

    def chat_conversation(self, intent:str, chat_history: list):
        parameters = {
            "candidate_count": 1,
            "max_output_tokens": 2048,
            "temperature": 0.4,
            "top_p": 0.8,
            "top_k": 40
        }
        
        chat_model = ChatModel.from_pretrained("chat-bison-32k@002")
        chat = chat_model.start_chat(
            context=self.prompts[intent]+str(chat_history)
        )
        return chat.send_message(self.query, **parameters).text