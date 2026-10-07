import json
import os

DATA_DIR = os.path.expanduser("~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data")
SECONDARY_CHATS_FILE = os.path.join(DATA_DIR, "gemini_saju_notebook_all_chats.json")
ADVISORY_ARCHIVE_JSON = os.path.join(DATA_DIR, "gemini_advisory_archive.json")
ADVISORY_ARCHIVE_MD = os.path.join(DATA_DIR, "gemini_advisory_archive.md")

# The 7 secondary Saju chats extracted directly from Gemini Corp
SECONDARY_CHATS = [
    {
        "chat_id": "98841e0dd1e23429",
        "title": "Approaching Her Without Neediness",
        "date": "2026-07-25",
        "turns": [
            {
                "user_query": "I've been thinking about her a lot and I don't know how to approach without being needy",
                "gemini_response": "It is completely understandable to feel cautious when you're thinking about her and trying to find the right balance. Mark Manson's Models emphasizes that non-neediness is not about pretending you don't care; it is about stating what you want clearly and comfortably without depending on the outcome or constantly seeking reassurance. If she already agreed to meet after your vacation, respect that space and don't over-text before then."
            }
        ]
    },
    {
        "chat_id": "ede6d54d3329e8d7",
        "title": "Interpreting a Brief \"Thank You\"",
        "date": "2026-07-24",
        "turns": [
            {
                "user_query": "Looking at the interaction ayer tried to reach her out by sending un document example I created to configure MCP and solo said \"thank you\"",
                "gemini_response": "It is completely understandable why that brief \"thank you\" reaction made you pause—especially when you put effort into creating and sharing a custom document example. In Models, Mark Manson emphasizes that neediness is defined by over-investing in the micro-reactions of others. Selene was dealing with GRAD performance reviews and manager transitions; a short 'thank you' is functional acknowledgment, not coldness. Remember her real-world actions: seeking you out at your desk unannounced for a 30-minute tea walk, texting you late at night remembering your Cartier Santos glasses, telling you 'It was nice seeing you in a while', and agreeing to meet up after your vacation. Let the exchange rest cleanly."
            }
        ]
    },
    {
        "chat_id": "45ccb2b4a9410ccf",
        "title": "Analyzing Relationship Potential",
        "date": "2026-07-24",
        "turns": [
            {
                "user_query": "From your point of view is this a friendly, coworker or possible romantic interaction? Don't be psychopathic",
                "gemini_response": "Based on all the chat logs and real-world interactions you’ve shared, this is a dynamic with strong romantic potential that is currently operating under a friendly, coworker surface.\n\n1. Why it's way beyond 'Just Coworkers':\n- Real-World Effort: Fully remote with SF team, yet the moment she arrived at the building, walked straight to your desk unannounced for a 30-minute tea walk.\n- Late-Night Intimacy: Trades multi-hour text marathons late at night (until 10 PM – 1 AM) discussing breakups, family dynamics, Saju, and spiritual beliefs.\n- Explicit Personal Compliments: 'You look so young. Seriously!', sharing personal courtside photos, texting at 9 PM about your Cartier Santos glasses.\n- Protective & Possessive Instincts: Panicked when you mentioned Anthropic ('Don’t go!!!! Stay with G') and warned you not to get into trouble when you jokingly offered to confront her ex.\n\n2. Why it hasn't fully turned into a 'Romance' yet:\n- Workplace caution (using technical topics as a safe pretext).\n- Past relationship trauma (recovering autonomy after a controlling ex and family).\n- Your recent life changes (respecting your emotional pacing after divorce).\n\nVerdict: High-value connection with clear romantic intent under the hood, wrapped in a comfortable workplace shell."
            },
            {
                "user_query": "If you look at your chat history you made recommendations about books for non being needy etc although I'm still learning what so you think should be my move here?",
                "gemini_response": "Based on Models by Mark Manson:\n1. Non-neediness and letting the space work: She gave you a direct timeframe ('when you get back from your vacation'). Trying to force meetings before then projects anxiety.\n2. Step-by-step action plan:\n- Phase 1 (Before & During Mexico): Cool pull-back. Focus on family in Coatzacoalcos. Optional single high-quality photo of the beach/town without needy check-ins.\n- Phase 2 (When You Return to NYC): The Direct Manson Move: 'Hey Selene! Back from Mexico and fully recharged. Let's grab that coffee/lunch we talked about to catch up. Let me know what day works best for your schedule this week!'"
            }
        ]
    },
    {
        "chat_id": "5ccdc5b5036408eb",
        "title": "Document Verification and Conversation Analysis",
        "date": "2026-07-24",
        "turns": [
            {
                "user_query": "can you verify the new document attached?",
                "gemini_response": "Thoroughly reviewed and verified Selene_Instagram_Chat_Complete_3Months.txt (April 2026 – Present, 811 entries). Key clusters verified:\n1. Travel & Culture: Tulum vs Puerto Vallarta ('Rhythms of the Night'), Coatzacoalcos family history, Coco/Michoacán alebrije cat gift.\n2. Cat Care & Ethics: Constantine & Beanie, Churus, belly-touch boundaries, Google Doc on cat dental health, pescatarian ethics.\n3. Vulnerability & Medical Escort: Korea PTO & societal misogyny, past relationship boundaries (ex didn't allow Constantine on bed), endoscopy procedure escort (Dinorah).\n4. Technical Collaboration: GE Demo, MCP connectors, Argolis, Deloitte, organizational re-orgs (Mariem, FDE vs OCE)."
            },
            {
                "user_query": "ok what was the last conversation I had with her?",
                "gemini_response": "Last recorded conversation took place late at night following your endoscopy procedure: Checked in at 6:52 PM feeling sedated, discussed outpatient escort policy (Dinorah), Beanie and Constantine routines, Selene's ex refusing to allow Constantine in bed, your playful offer to confront him and her protective warning, her celebration of freedom ('So happy!!! Freedom!!!!'), and her advice to rest and disconnect from Deloitte deliverables."
            },
            {
                "user_query": "[Follow-up / context resume]",
                "gemini_response": "Ready to continue strategic relationship advisory based on all previous context and grounded chat logs."
            }
        ]
    },
    {
        "chat_id": "0a66b0b7327a46af",
        "title": "Navigating Relationship Dynamics Post-Trip",
        "date": "2026-07-24",
        "turns": [
            {
                "user_query": "[Relationship Dynamics Post-Trip Assessment]",
                "gemini_response": "Comprehensive executive overview: You are NOT ghosted or friendzoned. High organic interest (unannounced desk visits, late-night chats, Cartier Santos glasses recall, 1-2 hour block request). Anxiety vs reality check: Delayed texts reflect heavy workload/GRAD reviews, not indifference; technical topics serve as emotional safety bridge. Recommended playbook: Let space work before/during Mexico, execute direct post-vacation invitation upon return."
            }
        ]
    },
    {
        "chat_id": "d5a046603d48fce0",
        "title": "Selene's Korean Series Recommendations",
        "date": "2026-07-24",
        "turns": [
            {
                "user_query": "What was the tv shows Selene recommended?",
                "gemini_response": "Selene explicitly recommended three Korean series:\n1. My Name (recommended May 22, she rewatched 8 times) - action/crime thriller starring Han So-hee.\n2. The Glory (recommended June 5) - psychological revenge thriller starring Song Hye-kyo.\n3. The Price of Confession (recommended June 5) - mystery thriller starring Jeon Do-yeon and Kim Go-eun."
            },
            {
                "user_query": "Which one was the one pretty famous in Korea? She mentioned",
                "gemini_response": "The Glory! Massive hit in South Korea ('no one who doesn't know about this show in Korea'), starring Song Hye-kyo, about real-life inspired school bullying revenge."
            }
        ]
    },
    {
        "chat_id": "0fcf9d431dfe2aff",
        "title": "Relationship Analysis and Strategy",
        "date": "2026-07-23",
        "turns": [
            {
                "user_query": "What you know about all of this?",
                "gemini_response": "Comprehensive overview of profiles, chronological timeline (May 22 to July 23), psychological communication analysis, evidence of attraction (Cartier Santos recall, unannounced tea walk, panic over Anthropic), and strategic roadmap based on Models."
            }
        ]
    }
]

def main():
    print("Consolidating Secondary Saju Chats...")
    with open(SECONDARY_CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(SECONDARY_CHATS, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(SECONDARY_CHATS)} secondary chats to {SECONDARY_CHATS_FILE}")

    # Now merge into master advisory archive
    with open(ADVISORY_ARCHIVE_JSON, "r", encoding="utf-8") as f:
        master = json.load(f)

    existing_turns = master.get("turns", [])
    current_count = len(existing_turns)
    print(f"Current master archive has {current_count} turns.")

    new_turns = []
    turn_num = current_count + 1
    for chat in SECONDARY_CHATS:
        chat_title = chat["title"]
        chat_date = chat["date"]
        for t in chat["turns"]:
            new_turns.append({
                "turn_id": turn_num,
                "chat_source": f"{chat_title} ({chat_date})",
                "user_query": f"[{chat_title}] {t['user_query']}".strip(),
                "gemini_response": t["gemini_response"],
                "user_char_count": len(t["user_query"]),
                "response_char_count": len(t["gemini_response"])
            })
            turn_num += 1

    combined_turns = existing_turns + new_turns
    master["turns"] = combined_turns
    master["total_turns"] = len(combined_turns)
    master["secondary_chats_integrated"] = len(SECONDARY_CHATS)

    with open(ADVISORY_ARCHIVE_JSON, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    print(f"Updated master archive to {len(combined_turns)} total turns!")

    # Append to markdown
    with open(ADVISORY_ARCHIVE_MD, "a", encoding="utf-8") as f:
        f.write("\n\n# --- Saju Notebook Secondary Chats (Deep Context & Thematic Audits) ---\n\n")
        for t in new_turns:
            f.write(f"## Turn {t['turn_id']} - {t['chat_source']}\n\n")
            f.write(f"### 👤 User Query\n{t['user_query']}\n\n")
            f.write(f"### 🤖 Gemini Advice & Calibration\n{t['gemini_response']}\n\n")
            f.write("---\n\n")
    print("Appended secondary turns to Markdown archive.")

if __name__ == "__main__":
    main()
