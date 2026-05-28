# streamAssist grounding visibility

Captured against `jira-testing_1778158449701` (Jira federated). Sample raw response: `sample_event_capture.json` (question: "List bugs in project SMP", 20 chunks).

## What IS exposed

- **`answer.diagnosticInfo.plannerSteps[]`** — full planner trace.
  - `queryStep.parts[].text` — the user query as seen by the planner.
  - `planStep.parts[].functionCall.{functionName, args, functionId}` — every tool call. We saw `selfawareness_agent({"request": "..."})`. The function ARGS are visible.
  - `planStep.parts[].text` — interleaved model reasoning chunks (the "thinking out loud" between tool calls).
  - `planStep.role` — `MODEL` for model-side steps.
- **`answer.replies[].groundedContent.textGroundingMetadata`** when a reply is actually grounded:
  - `references[].documentMetadata.{uri, title, document, domain, pageIdentifier, mimeType}` — full source identity, including the underlying datastore document resource name.
  - `references[].content` — the **actual chunk text** that was retrieved (the snippet the model saw).
  - `segments[].{text, endIndex, referenceIndices[]}` — which sentence-range of the reply maps to which reference index.
- **`answer.replies[].groundedContent.content.thought: true`** — chain-of-thought deltas are tagged separately from user-visible deltas, so we can hide/show them.
- **`answer.intentClassifications[]`** — e.g. `["SUPPORT"]`, the planner's intent label.
- **`answer.adkAuthor`** — which sub-agent produced the reply (`root_agent`, etc.).
- **`assistToken`** + **`sessionInfo.{session, queryId}`** — correlation handles for logging.

## What is MISSING

- **No per-source confidence / relevance score.** `references[]` has no `score`, `relevance`, or `confidence` field.
- **No tool RESPONSE.** We see the `functionCall` args, but never the result the function returned — only the model's subsequent `text` chunks. There is no `functionResponse` part in `plannerSteps`.
- **No JQL / native search query exposed.** The planner only logs the natural-language `request` it passed to `selfawareness_agent`, not whatever JQL or REST call that sub-agent ultimately built.
- **No datastore-routing decision trace.** With 15 datastores attached, the response never reveals *which* datastore(s) the planner consulted, or why one was preferred over another.
- **No raw retrieval candidates.** Only the `references[]` that survived into the final grounded answer are visible — not the rejected top-K.
- **No latency-per-step breakdown.** `createTime` per plan step lets us derive it client-side, but there is no explicit `tool_latency_ms` field.
- **No `citationMetadata` / `groundingMetadata` field at the Gemini API level.** GE uses its own `textGroundingMetadata` shape, not the one Gemini direct callers may know.

## Practical implications for the demo

- Inspector pane can show: "planner step N → called `selfawareness_agent` with X → wrote chunks Y" and per-reference chips with title+URL+chunk preview. That is enough to satisfy "why this source" at the human level.
- It CANNOT show: a numeric relevance score, the tool's raw return value, or per-datastore routing — those would require either logging on the connector side or a future GE feature.
