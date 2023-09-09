```mermaid
flowchart LR
  subgraph TOP
    direction TB
    subgraph B1
        direction RL
        i1 -->f1
    end
    subgraph B2
        direction BT
        i2 -->f2
    end
  end
  A --> TOP --> B
  B1 --> B2
  ```





```mermaid
graph TB
        A[Google Cloud Storage] ---> |train.csv| B[Tensor]
    subgraph  ""
        direction TB
        B -- "feature engineering" --> C[Normalization]
        B -- "feature engineering" --> D[Categorical Encoding]
        C --> E[Concatenation]
        D --> E
        E --> F(Neural Network)
        id1{{aiplatform.CustomJob}}
    end
        F --> |model save| G[Google Cloud Storage]
```