import json
import os

DATA_DIR = os.path.expanduser("~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data")
DESKTOP_DIR = os.path.expanduser("~/Desktop")
DESKTOP_IG = os.path.join(DESKTOP_DIR, "Selene_Instagram_Complete_Chat_History.json")
OUT_IG = os.path.join(DATA_DIR, "instagram_live_complete.json")

def main():
    print("Reading Desktop base Instagram history...")
    with open(DESKTOP_IG, "r", encoding="utf-8") as f:
        messages = json.load(f)

    print(f"Loaded {len(messages)} historical Instagram messages.")

    # Live messages captured from Chrome tab on September 9, 2026 (California / Bay View visit)
    sept9_messages = [
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:50:00",
            "type": "text",
            "text": "I know",
            "reactions": []
        },
        {
            "sender": "Jesus Chavez",
            "date": "2026-09-09 13:51:00",
            "type": "text",
            "text": "Have you had the chance to stay at the Bay View Suites, the Google hotel located near the new Google campus?",
            "reactions": []
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:51:15",
            "type": "text",
            "text": "🥲🥲🥲",
            "reactions": []
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:51:30",
            "type": "text",
            "text": "Yes",
            "reactions": []
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:51:45",
            "type": "text",
            "text": "It was way too small",
            "reactions": []
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:52:00",
            "type": "text",
            "text": "Tetra hotel is amazing",
            "reactions": []
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:52:15",
            "type": "text",
            "text": "Love love love",
            "reactions": [{"user": "Jesus Chavez", "emoji": "❤️"}]
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:52:30",
            "type": "text",
            "text": "Meet my standard",
            "reactions": [{"user": "Jesus Chavez", "emoji": "😂"}]
        },
        {
            "sender": "Jesus Chavez",
            "date": "2026-09-09 13:53:00",
            "type": "text",
            "text": "Agree! So small, lucky me I got used to small spaces",
            "reactions": [{"user": "Selene Song", "emoji": "😂"}]
        },
        {
            "sender": "Jesus Chavez",
            "date": "2026-09-09 13:53:20",
            "type": "text",
            "text": "Oh! Tetra! Loved it! I stayed couple of times!",
            "reactions": [{"user": "Selene Song", "emoji": "❤️"}]
        },
        {
            "sender": "Jesus Chavez",
            "date": "2026-09-09 13:53:40",
            "type": "text",
            "text": "Yes yes yes",
            "reactions": []
        },
        {
            "sender": "Jesus Chavez",
            "date": "2026-09-09 13:54:00",
            "type": "text",
            "text": "So I decided the bay mostly because of the Google gym (Edited)",
            "reactions": []
        },
        {
            "sender": "Jesus Chavez",
            "date": "2026-09-09 13:54:30",
            "type": "photo_attachment",
            "text": "But got this last night",
            "media": "bay_view_night_photo",
            "reactions": [{"user": "Selene Song", "emoji": "❤️"}]
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:55:00",
            "type": "text",
            "text": "Nice!",
            "reactions": []
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:55:15",
            "type": "text",
            "text": "I liked the area",
            "reactions": []
        },
        {
            "sender": "Selene Song",
            "date": "2026-09-09 13:55:30",
            "type": "text",
            "text": "Beautiful view of new office",
            "reactions": [{"user": "Jesus Chavez", "emoji": "❤️"}]
        }
    ]

    all_messages = messages + sept9_messages
    print(f"Appended {len(sept9_messages)} live messages from Sept 9. Total: {len(all_messages)}")

    with open(OUT_IG, "w", encoding="utf-8") as f:
        json.dump(all_messages, f, indent=2, ensure_ascii=False)

    print(f"Saved complete merged Instagram archive to: {OUT_IG}")

if __name__ == "__main__":
    main()
