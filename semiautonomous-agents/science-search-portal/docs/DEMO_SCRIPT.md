# Demo Script — Amgen Science Search Portal

A presenter's script for a 12–18 minute live demo. Each section has a **stage direction** (what to do), a **say** (verbatim talking points), and **why it matters** (in case anyone asks).

Pair with `SECURITY_FLOW.md` for the architecture deep-dive.

---

## 0. Pre-flight checklist (do 5 minutes before)

- [ ] Frontend running on `http://localhost:5173` — open in a clean Chrome window, no extensions visible
- [ ] Backend running on `:8001` (auto-reload enabled)
- [ ] Logged in as `admin@sockcop.onmicrosoft.com`
- [ ] Send one warmup query (e.g., "What is AIMOVIG?") so the backend is hot, the JWT is fresh, and the model has cached state
- [ ] Confirm the **ACL trust strip** under the header shows: `Showing results for admin@sockcop · 5 connectors in scope · STS valid Xm`
- [ ] Open a second browser tab to `https://sockcop.sharepoint.com` (you may need to switch to it briefly during Phase D, to prove docs exist on the SP side)
- [ ] Have `SECURITY_FLOW.md` open in a side window for any deep-dive questions

> If any **trap question** (Tezspire / Repatha price / biosimilars) is on your script, do NOT pre-warm those — the audience needs to see the model say "I don't know" live.

---

## 1. The opening (1 min) — set the stakes

**Stage:** Portal is on screen, logged in, conversation panel empty.

**Say:**
> "What you'll see today is Amgen's product knowledge — the actual prescribing information, medication guides, and instructions for use that you publish — being made queryable through a single conversation. Every answer you'll see comes back from your live SharePoint, filtered against my user's permissions in real time. There is no copy of your data sitting in Google's index. Every citation traces to a specific document, and the entire authentication chain is per-user, end-to-end. Let me show you."

**Why it matters:**
- Frames the demo as *trust + grounding*, not *AI cleverness*.
- Establishes upfront: **per-user**, **live**, **traceable**. These are the three things Med Affairs and Regulatory will judge you on.

---

## 2. Demo question 1 — *"What is AIMOVIG?"* (the opener) (1.5 min)

**Stage:** Click the welcome-screen button **"What is AIMOVIG?"** (or type it).

**While loading, say:**
> "Watch the latency badge — you'll see it break down: STS token exchange, Discovery Engine federation, then generation. None of this is cached."

**When the response appears:**

- Point at the source chips below the answer (numbered 1, 2, 3).
- Click chip [¹] — the source preview drawer slides in from the right.

**Say:**
> "Three citations from your SharePoint — the prescribing information, the patient information, and the instructions for use. I'll click one — there's the actual snippet from the document, and an 'Open in SharePoint' button that takes me straight to the file in your tenant. The model didn't make this up. It came from your label."

**Why it matters:**
- First grounded answer with multiple sources lands the "real grounding" claim.
- The source drawer is the Veeva-Vault-like familiar workflow Med Affairs trusts.

---

## 3. Demo question 2 — *"How does Repatha work?"* (mechanism, 1.5 min)

**Stage:** Type or use a follow-up chip if available.

**Say:**
> "Same pattern, different angle — this is the kind of question your Medical Science Liaisons get every day. Watch how the model answers strictly from the label, not from training data."

**When the response appears:**
- Point at the inline `[¹]` superscripts in the answer text.
- Click one — drawer opens to the cited paragraph.

**Say:**
> "Notice the inline citations — this isn't 'I read three documents and generated something'. Each sentence in the answer is traceable to a specific paragraph. If your regulatory team needs to audit a claim, the link is right there."

**Why it matters:**
- Per-claim traceability — "audit-ready" framing that lands with Regulatory.

---

## 4. Demo question 3 — *"Otezla renal impairment dose"* (the kill shot, 2 min)

**Stage:** Type the question. **Wait through the ~22s latency.** Don't fill the silence with "the demo is loading" — let it run.

**While it loads, click the Shield icon in the ACL strip.** The Auth Flow overlay appears.

**Say (while overlay is visible):**
> "This is a good moment to show you what's actually happening behind the answer you're about to see. Here's the security chain: Microsoft Entra checks who I am, my identity is exchanged at Google's STS endpoint via Workload Identity Federation — you can see the WIF pool name there. Discovery Engine then talks to the SharePoint connector using the OAuth refresh token I personally consented to. SharePoint applies its normal per-document ACLs. The grounded response comes back. No service-account anywhere. No sync of your data into Google. Live, every query."

**Close the overlay. The answer is now ready.**

**Say (when answer is visible):**
> "Six citations from the Otezla prescribing information — the renal impairment dose-adjustment table specifically. This is the kind of clinical depth your Med Affairs team would expect from a trained MSL, surfaced in twenty seconds with full traceability."

**Why it matters:**
- Six grounding refs in one answer — the heaviest grounding flex in the corpus.
- Pairing the kill-shot question with the Auth Flow overlay turns a latency liability into a demo asset.
- "Live, every query" is the differentiator vs. RAG-on-cached-vector-store competitors.

---

## 5. Demo question 4 — *"Compare Prolia and Xgeva dosing"* (multi-product synthesis, 2 min)

**Stage:** Type the question.

**Say:**
> "Both of these are denosumab — same molecule, different indications, different dosing. This is where the agent has to find information across two separate documents and synthesize. Watch."

**When the response appears (a Markdown table):**
- Point at the two source chips (one Prolia, one Xgeva).

**Say:**
> "Side-by-side comparison from two distinct labels, returned as a clean table — and again, two citations. This is the kind of cross-product question that breaks most retrieval systems because they can't reason across documents. Here, we can."

**Why it matters:**
- Multi-document synthesis is the AI capability that distinguishes this from a search box.
- The Markdown table is a visual win — looks like a slide.

---

## 6. Trust closer — *"What does our SharePoint say about Tezspire?"* (the trap, 1 min)

**Stage:** Type the question. Tezspire is intentionally NOT in the corpus.

**While loading, say:**
> "One last thing. The single most important property for a system like this is *honesty when it doesn't know the answer*. So I'm going to ask about a product we deliberately didn't upload — Tezspire."

**When the response appears (something like "I was unable to find any information about Tezspire on your SharePoint"):**

**Say:**
> "Notice what it didn't do. It didn't pull from Wikipedia. It didn't pull from Amgen's public website. It didn't make up a plausible-sounding answer. It said: 'No, I don't have that document in my scope.' That's the model honoring the grounding rule we configured at the engine level. For Med Affairs, this is the property that makes the system deployable. Hallucination is the deal-breaker, and we don't have it."

**Why it matters:**
- Negative-control demonstration is the trust closer. Most demos hide failure cases; this is the failure case as the *feature*.

---

## 7. Optional (if time allows) — Agent panel (2 min)

**Stage:** Click the floating Agent button bottom-right. Panel opens.

**Say:**
> "What you've seen so far is a single grounded chat. What you're seeing now is an *agent* — same security model, same per-user ACL, but it can use multiple tools. It searches SharePoint internally, then also does a web search for context, and synthesizes both."

**Type or use the suggestion:** *"Compare AIMOVIG internal docs vs public info"*

**While loading, say:**
> "This is going to take longer because there's more orchestration — and the same security guarantees apply. The agent runs on Vertex AI Agent Engine, but the SharePoint call is still made as me. The Agent Engine doesn't get to bypass the ACL."

**When response appears:**
- Show the side-by-side internal vs external content.

**Why it matters:**
- Demonstrates the platform extends beyond chat to agentic workflows without breaking the security model.

---

## 8. The close (1 min)

**Stage:** Bring the ACL strip back into focus by pointing at it.

**Say:**
> "Three things to take away:
> 1. **Per-user ACL is enforced live, every query.** Not at index time, not via a snapshot — at query time, using my Microsoft identity, against your live SharePoint.
> 2. **Every answer cites the source, paragraph by paragraph.** Audit-ready by design.
> 3. **When the system doesn't know, it says so.** No hallucination, no invented references, no plausible-sounding fabrication.
> "Together, these three properties are what make this deployable for a company like Amgen, where 'mostly right' isn't good enough."

---

## 9. Likely Q&A (anticipate and prepare)

| Question | Short answer | Full answer in |
|---|---|---|
| "Where is the data stored?" | Nothing about your documents is persisted in Google. The connector reads SharePoint live each time. | `SECURITY_FLOW.md` §1 + §5 |
| "Can a service account read documents?" | No — the system requires a user JWT. Without it, no SharePoint OAuth token can be looked up. | §5 + §6 |
| "What if a user is removed from a SharePoint site?" | Next query returns nothing for that site. No cached bypass. | §5 |
| "How is this different from Microsoft Copilot?" | Same per-user grounding promise; this runs on Google Cloud Gemini Enterprise with full transparency into the chain (you saw the auth flow), and the same backend is consumable by your agentic workflows on Vertex AI. | n/a — your call |
| "What's the latency story for production?" | Median 13–14 seconds today against your sandbox tenant. Production-tuned: connection pooling, regional endpoints, fewer entity datastores per query. Realistic 5–8s steady-state. | n/a |
| "How do we add a new SharePoint site to scope?" | One API call to PATCH the connector's `admin_filter.Site`. Federated connectors don't need a re-sync — next query picks it up. | §5 + §6 |
| "Can it write back to SharePoint?" | Yes — the connector has `actionConfig` enabled with `create_folder`, `add_page`, `upload_document`, `add_list`, `check_in/out_document`, etc. The chat side is read-only today; agentic actions are a small extension. | §1 |

---

## 10. Recovery — what to do if something breaks live

| If… | Do… |
|---|---|
| A query returns "0 grounding refs" / refusal | Don't dwell. Say "the model occasionally refuses queries that look like medical advice — let me rephrase" and use the `"How does X work?"` form instead. |
| The ACL strip disappears / shows 0 connectors | Refresh the page once. JWT may need to be re-acquired. If still broken, fall back to the screenshots in `/tmp/` or skip to the agent panel. |
| The Auth Flow overlay won't open | Use Shift+S as a fallback. If still broken, open `SECURITY_FLOW.md` in another tab and walk through the diagram there. |
| The whole portal is down | Pivot to the architecture story — open `SECURITY_FLOW.md` and walk the audience through the diagrams. The story is the deliverable, the demo is the proof. |
| You get a question you can't answer | "Let me follow up on that — can I get your email so I make sure I get you the right answer?" Always better than guessing. |

---

## 11. Demo arc summary (the one-glance cheat sheet)

| # | Question | Why we ask it | Expected refs | ~Latency |
|---|---|---|---|---|
| 1 | What is AIMOVIG? | Multi-source grounded opener | 3 | 12–16s |
| 2 | How does Repatha work? | Mechanism, MSL-style | 2 | ~16s |
| 3 | Otezla renal impairment dose | Kill shot — 6 refs, clinical depth | 6 | ~22s |
| 4 | Compare Prolia and Xgeva dosing | Multi-product synthesis (table) | 2 | ~23s |
| 5 | What does our SharePoint say about Tezspire? | Trap — proves no hallucination | 0 (clean refusal) | ~10s |
| 6 *(optional)* | Compare AIMOVIG internal docs vs public info | Agent path with web search | 2+ | ~25s |

Total: ~2 minutes of waiting for ~6 minutes of talking — fine if you fill the latency with the Auth Flow overlay during question #3.

---

*Built for the Amgen demo by the Amgen Science Search Portal team. Architecture details in `SECURITY_FLOW.md`.*
