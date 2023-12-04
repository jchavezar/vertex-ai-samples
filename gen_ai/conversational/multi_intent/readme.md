## Multi-Intent Chatbot

For intent detection temperature, top_k and top_p were lowered to raise the level of accuracy in the desired output, for chat bot based in intent detection chat-bison@latest was used.

```mermaid
graph TD;
    human -- "task: detect_intent" --> bot(bot: intent detected);
    id1[[intent_types:
    - aos_navigator
    - analytics_assets
    - analytics_products
    - analytics_campaigns
    - default_intent
    ]];

    bot -- "default_intent" --> greetings(bot: any topic);
    bot -- "analytics_products" --> account_support(bot: account support);
    bot -- "analytics_campaigns" --> product_prices(bot: product prices);
    bot -- "aos_navigator" --> marketing_campaigns(bot: campaigns);
```

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```



```mermaid
graph TD;
    human -- "task: detect_intent" --> bot(bot: intent detected);
    id1[[intent_types:
    - aos_navigator
    - analytics_assets
    - analytics_products
    - analytics_campaigns
    - default_intent
    ]];
```