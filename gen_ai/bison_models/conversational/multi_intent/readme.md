## Multi-Intent Chatbot

For intent detection temperature, top_k and top_p were lowered to raise the level of accuracy in the desired output, for chat bot based in intent detection chat-bison@latest was used.

```mermaid
graph TB
    human:::foo -- "task: detect_intent" --> bot(bot: intent detected):::bar
    classDef foo stroke:#f00
    classDef bar stroke:#00f

    bot -- "default_intent" --> greetings(bot: any topic):::foobar
    bot -- "account_support" --> account_support(bot: profile, billing):::foobar
    bot -- "product_prices" --> product_prices(bot: info and price):::foobar
    bot -- "marketing_campaigns" --> marketing_campaigns(bot: campaigns):::foobar
    classDef foobar stroke:#0f0
```