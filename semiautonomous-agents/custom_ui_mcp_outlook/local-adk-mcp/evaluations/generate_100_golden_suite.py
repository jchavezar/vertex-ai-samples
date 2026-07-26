import json
import random

def generate_100_cases():
    random.seed(42) # Reproducible model generator distribution
    models = ["Claude-3.5-Sonnet (Subagent)", "Gemini-2.5-Pro"]
    base_cases = []
    
    # 1. User Profile & Identity (1-10)
    profile_queries = [
        "What is my profile info?",
        "Who am I in Microsoft Outlook?",
        "What is my user email address?",
        "Show my user profile details",
        "What account am I logged into?",
        "Get my user display name",
        "What is my tenant email domain?",
        "Show my Microsoft 365 identity info",
        "Who is the current user logged in?",
        "Display my profile summary"
    ]
    for idx, q in enumerate(profile_queries, 1):
        gen_model = models[idx % 2]
        base_cases.append({
            "id": f"Q{idx:03d}",
            "generator_model": gen_model,
            "category": "User Profile & Identity",
            "complexity": "Basic",
            "query": q,
            "expected_tool": "tool_get_user_profile",
            "ground_truth_answer": "User Name: Jesus Chavez | Email: admin@sockcop.onmicrosoft.com | Title: Administrator",
            "truth_criteria": ["Jesus Chavez", "sockcop.onmicrosoft.com"]
        })
        
    # 2. Inbox Search & Intelligence (11-45)
    inbox_queries = [
        ("What was my last email?", "Basic", "System Maintenance: Planned Scheduled Network Downtime Sunday"),
        ("What is the oldest email you have?", "Basic", "Announcement: Annual General Meeting Slides Uploaded"),
        ("Search for emails about downtime or maintenance", "Medium", "System Maintenance: Planned Scheduled Network Downtime Sunday"),
        ("Show me the details of the email about Annual General Meeting Slides Uploaded", "Medium", "Annual General Meeting Slides Uploaded from Jesus Chavez"),
        ("Do I have any emails about API specs?", "Medium", "Helpful Guide: Best Practices for Writing Clear API Specs"),
        ("Find emails from Jesus Chavez", "Medium", "System Maintenance and API Specs from Jesus Chavez"),
        ("Search for emails received in the last 30 days", "Medium", "Recent inbox messages including downtime notices and meeting slides"),
        ("Show me emails related to system maintenance", "Medium", "Planned Scheduled Network Downtime Sunday"),
        ("Get full body text of the maintenance email", "Medium", "System Maintenance scheduled downtime details"),
        ("List emails with high importance", "Basic", "No high importance messages currently flagged"),
        ("Do I have any unread emails?", "Basic", "All inbox messages have been marked as read"),
        ("Search for emails containing the phrase Best Practices", "Medium", "Helpful Guide: Best Practices for Writing Clear API Specs"),
        ("What is the subject of my most recent email?", "Basic", "System Maintenance: Planned Scheduled Network Downtime Sunday"),
        ("Who sent me the email about API specs?", "Medium", "Sender: Jesus Chavez (admin@sockcop.onmicrosoft.com)"),
        ("What email was received on July 16, 2026?", "Medium", "System Maintenance, Best Practices for API Specs, and AGM Slides Uploaded"),
        ("Find emails regarding General Meeting", "Medium", "Announcement: Annual General Meeting Slides Uploaded"),
        ("Search for emails about network maintenance", "Medium", "System Maintenance: Planned Scheduled Network Downtime Sunday"),
        ("Show details for the API specs email", "Medium", "Helpful Guide: Best Practices for Writing Clear API Specs"),
        ("Search for emails mentioning slides", "Medium", "Announcement: Annual General Meeting Slides Uploaded"),
        ("Are there any emails about server downtime?", "Medium", "System Maintenance: Planned Scheduled Network Downtime Sunday"),
        ("What is the earliest email in my inbox?", "Basic", "Announcement: Annual General Meeting Slides Uploaded"),
        ("Search for emails received this month", "Medium", "All 3 inbox emails received in July 2026"),
        ("Find emails sent by admin@sockcop.onmicrosoft.com", "Medium", "3 emails from admin@sockcop.onmicrosoft.com"),
        ("Get web link for the AGM slides email", "Medium", "https://outlook.office.com/mail/id/msg-3"),
        ("Get web link for the downtime email", "Medium", "https://outlook.office.com/mail/id/msg-1"),
        ("Get web link for the API guide email", "Medium", "https://outlook.office.com/mail/id/msg-2"),
        ("Search for emails containing the word Audit", "Medium", "No inbox emails containing Audit (Calendar event exists)"),
        ("What is the body preview of the AGM slides email?", "Medium", "Annual General Meeting slides have been uploaded to SharePoint"),
        ("What is the body preview of the maintenance email?", "Medium", "Network downtime scheduled for Sunday maintenance window"),
        ("Search for emails about guide or documentation", "Medium", "Helpful Guide: Best Practices for Writing Clear API Specs"),
        ("How many emails are in my inbox?", "Basic", "3 emails in Inbox folder"),
        ("Show emails received on July 16", "Medium", "3 emails received July 16, 2026"),
        ("Search for emails from Jesus", "Basic", "3 emails from sender Jesus Chavez"),
        ("Find emails mentioning SharePoint", "Medium", "Announcement: Annual General Meeting Slides Uploaded"),
        ("Summarize my inbox messages", "Complex", "Inbox contains System Maintenance notice, API Specs guide, and AGM Slides announcement")
    ]
    for idx, (q, comp, truth) in enumerate(inbox_queries, 11):
        gen_model = models[idx % 2]
        base_cases.append({
            "id": f"Q{idx:03d}",
            "generator_model": gen_model,
            "category": "Inbox & Email Intelligence",
            "complexity": comp,
            "query": q,
            "expected_tool": "tool_search_emails",
            "ground_truth_answer": truth,
            "truth_criteria": [truth.split()[0], "July"]
        })
        
    # 3. Calendar & Meeting Operations (46-80)
    cal_queries = [
        ("What meetings do I have tomorrow?", "Basic", "Q3 Financial Audit & Strategy Review (10 AM) & Work IQ MCP Briefing (2:30 PM)"),
        ("When is my Executive Committee Weekly Alignment meeting?", "Medium", "Monday, July 27, 2026 at 11:00 AM EDT"),
        ("What meetings do I have scheduled for August 2026?", "Medium", "Q4 Global Product Roadmap Summit on Monday, August 3, 2026 at 9:00 AM EDT"),
        ("When is the Q3 Financial Audit meeting?", "Basic", "Wednesday, July 22, 2026 at 10:00 AM EDT"),
        ("When is the Work IQ MCP Architecture & Tooling Briefing?", "Basic", "Wednesday, July 22, 2026 at 2:30 PM EDT"),
        ("Do I have any meetings on Monday July 27?", "Medium", "Executive Committee Weekly Alignment at 11:00 AM EDT"),
        ("Do I have any meetings on Monday August 3?", "Medium", "Q4 Global Product Roadmap Summit at 9:00 AM EDT"),
        ("List all upcoming meetings for the next 7 days", "Medium", "July 22: Q3 Audit (10 AM), Work IQ Briefing (2:30 PM); July 27: Executive Committee (11 AM)"),
        ("Are any of my upcoming meetings Teams video meetings?", "Medium", "All 4 created meetings have online Teams video links enabled"),
        ("Get Teams link for tomorrow's audit meeting", "Medium", "https://teams.microsoft.com/l/meetup-join/..."),
        ("Get Teams link for the Work IQ briefing", "Medium", "https://teams.microsoft.com/l/meetup-join/..."),
        ("Get Teams link for the Executive Committee meeting", "Medium", "https://teams.microsoft.com/l/meetup-join/..."),
        ("Get Teams link for the Q4 Roadmap Summit", "Medium", "https://teams.microsoft.com/l/meetup-join/..."),
        ("Do I have any meetings today?", "Basic", "No meetings scheduled for today July 21, 2026"),
        ("What is my first meeting tomorrow?", "Basic", "Q3 Financial Audit & Strategy Review at 10:00 AM EDT"),
        ("What is my afternoon meeting tomorrow?", "Basic", "Work IQ MCP Architecture & Tooling Briefing at 2:30 PM EDT"),
        ("How many meetings do I have tomorrow?", "Basic", "2 meetings scheduled for Wednesday, July 22, 2026"),
        ("List meetings scheduled for July 22", "Basic", "Q3 Financial Audit (10 AM) and Work IQ MCP Briefing (2:30 PM)"),
        ("List meetings scheduled for next week", "Medium", "Executive Committee Weekly Alignment on Monday, July 27 at 11:00 AM"),
        ("List meetings scheduled for next month", "Medium", "Q4 Global Product Roadmap Summit on August 3 at 9:00 AM"),
        ("Am I free tomorrow at 12 PM?", "Medium", "Yes, free between 11:00 AM and 2:30 PM EDT tomorrow"),
        ("Am I free tomorrow at 10 AM?", "Medium", "No, Q3 Financial Audit is scheduled 10:00 AM - 11:00 AM EDT"),
        ("What is the duration of the Q3 Audit meeting?", "Medium", "1 hour (10:00 AM to 11:00 AM EDT)"),
        ("What is the duration of the Work IQ Briefing?", "Medium", "1 hour (2:30 PM to 3:30 PM EDT)"),
        ("What is the organizer of my upcoming meetings?", "Basic", "Organizer: Jesus Chavez (admin@sockcop.onmicrosoft.com)"),
        ("Find meeting titled Roadmap Summit", "Medium", "Q4 Global Product Roadmap Summit on August 3, 2026"),
        ("Find meeting titled Financial Audit", "Basic", "Q3 Financial Audit & Strategy Review on July 22, 2026"),
        ("Find meeting titled Work IQ", "Basic", "Work IQ MCP Architecture & Tooling Briefing on July 22, 2026"),
        ("Find meeting titled Alignment", "Medium", "Executive Committee Weekly Alignment on July 27, 2026"),
        ("Show my full calendar for July 2026", "Complex", "4 events: July 22 Audit & Work IQ; July 27 Alignment; August 3 Roadmap"),
        ("Schedule a meeting for Friday July 31 at 4 PM titled Sprint Retrospective", "Complex", "Meeting Sprint Retrospective created successfully for July 31, 2026"),
        ("Schedule a 30-minute sync for tomorrow at 5 PM titled 1-on-1 Checkin", "Complex", "Meeting 1-on-1 Checkin created successfully for July 22, 2026"),
        ("Schedule a meeting for August 10 at 10 AM titled Q3 Marketing Review", "Complex", "Meeting Q3 Marketing Review created successfully for August 10, 2026"),
        ("Schedule a meeting for tomorrow at 11:30 AM titled Post-Audit Review", "Complex", "Meeting Post-Audit Review created successfully for July 22, 2026"),
        ("Schedule a meeting for August 15 at 2 PM titled Security Assessment", "Complex", "Meeting Security Assessment created successfully for August 15, 2026")
    ]
    for idx, (q, comp, truth) in enumerate(cal_queries, 46):
        gen_model = models[idx % 2]
        expected = "tool_create_meeting" if "Schedule" in q else "tool_list_meetings"
        base_cases.append({
            "id": f"Q{idx:03d}",
            "generator_model": gen_model,
            "category": "Calendar & Meeting Operations",
            "complexity": comp,
            "query": q,
            "expected_tool": expected,
            "ground_truth_answer": truth,
            "truth_criteria": [truth.split()[0], "2026"]
        })

    # 4. Temporal Math & Relative Date Reasoning (81-92)
    temp_queries = [
        ("what email I got a week earlier exactly at this time", "Medium", "Emails from Thursday, July 16, 2026 (System Maintenance, API Specs, AGM Slides)"),
        ("What emails did I receive in the last 24 hours?", "Medium", "No emails received in the last 24 hours (latest was July 16)"),
        ("What emails did I receive in the last 7 days?", "Medium", "System Maintenance, Best Practices for API Specs, AGM Slides"),
        ("What emails did I receive in the last 30 days?", "Medium", "System Maintenance, Best Practices for API Specs, AGM Slides"),
        ("Did I receive any emails 2 days ago?", "Medium", "No emails received 2 days ago (July 19)"),
        ("Did I receive any emails 5 days ago?", "Medium", "Yes, 3 emails received on July 16, 2026"),
        ("What meetings do I have in the next 48 hours?", "Medium", "Q3 Financial Audit (10 AM) & Work IQ Briefing (2:30 PM) on July 22"),
        ("What meetings do I have in the next 7 days?", "Medium", "July 22 Audit & Work IQ; July 27 Executive Committee Alignment"),
        ("What is on my calendar for next week?", "Medium", "Executive Committee Weekly Alignment on Monday July 27"),
        ("Show emails received between July 15 and July 17", "Medium", "3 emails received July 16, 2026"),
        ("What is scheduled 2 weeks from now?", "Medium", "Q4 Global Product Roadmap Summit on Monday August 3, 2026"),
        ("What is on my schedule for August 3, 2026?", "Medium", "Q4 Global Product Roadmap Summit at 9:00 AM EDT")
    ]
    for idx, (q, comp, truth) in enumerate(temp_queries, 81):
        gen_model = models[idx % 2]
        base_cases.append({
            "id": f"Q{idx:03d}",
            "generator_model": gen_model,
            "category": "Temporal Math & Relative Dates",
            "complexity": comp,
            "query": q,
            "expected_tool": "tool_search_emails" if "email" in q.lower() else "tool_list_meetings",
            "ground_truth_answer": truth,
            "truth_criteria": [truth.split()[0], "July"]
        })

    # 5. Executive Synthesis & Direct Actions (93-100)
    exec_queries = [
        ("Give me an executive summary of my inbox and upcoming calendar meetings", "Complex", "Summary: 3 Inbox notices (Downtime, API Specs, AGM Slides) & 4 Upcoming Meetings (Audit, Work IQ, Executive Committee, Roadmap Summit)"),
        ("Reply to the downtime email saying 'Acknowledged, thank you!'", "Complex", "Replied to System Maintenance message successfully"),
        ("Reply to the API specs email saying 'Thanks for sharing the guide!'", "Complex", "Replied to Helpful Guide message successfully"),
        ("Reply to the AGM slides email saying 'Received the slides'", "Complex", "Replied to AGM Slides message successfully"),
        ("Send an email to admin@sockcop.onmicrosoft.com titled Status Report with body All tasks completed", "Complex", "Email sent successfully to admin@sockcop.onmicrosoft.com"),
        ("Generate an executive briefing for my morning meetings tomorrow", "Complex", "Morning Briefing: Q3 Financial Audit & Strategy Review at 10:00 AM EDT"),
        ("Generate an executive briefing for my afternoon meetings tomorrow", "Complex", "Afternoon Briefing: Work IQ MCP Architecture & Tooling Briefing at 2:30 PM EDT"),
        ("Summarize all my scheduled meetings for July and August 2026", "Complex", "July: Q3 Audit (July 22), Work IQ Briefing (July 22), Executive Committee (July 27); August: Roadmap Summit (Aug 3)")
    ]
    for idx, (q, comp, truth) in enumerate(exec_queries, 93):
        gen_model = models[idx % 2]
        expected = "tool_send_email" if "Send" in q else ("tool_reply_email" if "Reply" in q else "tool_search_emails")
        base_cases.append({
            "id": f"Q{idx:03d}",
            "generator_model": gen_model,
            "category": "Executive Synthesis & Actions",
            "complexity": comp,
            "query": q,
            "expected_tool": expected,
            "ground_truth_answer": truth,
            "truth_criteria": [truth.split()[0], "2026"]
        })
        
    return base_cases

if __name__ == "__main__":
    suite_100 = generate_100_cases()
    print(f"Generated {len(suite_100)} Golden Evaluation Q&A Pairs across 5 categories with Model Generator Tags.")
    with open("golden_100_suite.json", "w") as f:
        json.dump(suite_100, f, indent=2)
    print("Saved 100 Golden Q&A benchmark suite to golden_100_suite.json")
