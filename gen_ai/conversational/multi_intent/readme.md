## Multi-Intent Chatbot

For intent detection temperature, top_k and top_p were lowered to raise the level of accuracy in the desired output, for chat bot based in intent detection chat-bison@latest was used.

```mermaid
graph TB
    human:::foo -- "task: detect_intent" --> bot(bot: intent detected):::bar
    classDef foo stroke:#f00
    classDef bar stroke:#00f
    id1[[intent_types:
    - aos_navigator
    - analytics_assets
    - analytics_products
    - analytics_campaigns
    - default_intent
    ]]

    bot -- "default_intent" --> greetings(bot: any topic):::foobar
    bot -- "analytics_products" --> account_support(bot: account support):::foobar
    bot -- "analytics_campaigns" --> product_prices(bot: product prices):::foobar
    bot -- "aos_navigator" --> marketing_campaigns(bot: campaigns):::foobar
    classDef foobar stroke:#0f0

    

    

```
