- You never push until something is working and tested by yourself.

## Autonomous Testing & Verification Rules
- **ALWAYS** perform active browsing or self-test the code autonomously after implementing a plan.
- If the test fails, debug and fix it autonomously. Ensure you verify the UX/UI and functionality thoroughly.

## Gemini Enterprise vs Agent Engine Deployment (CRITICAL)
- **Agent Engine** is the backend infrastructure (Reasoning Engine) where the code runs. Deploying to Agent Engine only exposes an API endpoint via Vertex AI.
- **Gemini Enterprise** is the consumer-facing user interface (agent builder/discovery engine). 
- **RULE:** If you are asked to deploy and register an agent, deploying to Agent Engine is NOT enough. You MUST also register the Reasoning Engine in the Gemini Enterprise App. If you cannot do this automatically, you MUST explicitly tell the user that they must go to the Gemini Enterprise Console to link the Reasoning Engine ID to complete the registration.

## Port Management & Conflict Prevention
To avoid port conflicts when running multiple Antigravity applications simultaneously, use the following strictly assigned ports:

| Application | Role | Port |
| :--- | :--- | :--- |
| **sharepoint_sentinel_mcp** | Backend | `8003` |
| **sharepoint_sentinel_mcp** | Frontend | `5171` |
| **multimodal_document_nexus** | Backend | `8001` |
| **multimodal_document_nexus** | Frontend | `5172` |
| **zero_leak_security_proxy** | Backend | `8002` |
| **zero_leak_security_proxy** | Frontend | `5175` |
| **market_swarm_terminal** | Backend | `8005` |
| **market_swarm_terminal** | Frontend | `5173` |
| **nexus_search_core** | Backend | `8006` |
| **nexus_search_core** | Frontend | `5174` |
| **internal_components_portal** | Backend | `8008` |
| **internal_components_portal** | Frontend | `5177` |

> [!IMPORTANT]
> Never use overlapping ports for Antigravity apps. Always check this section before assigning new ports to any application.
