import os
import json

def build_context_bundle(p):
    """Builds a rich context prompt for an AI agent turn."""
    lines = []
    lines.append(f"# 🚀 Project Context: {p['title']}")
    lines.append(f"- **Project Folder**: `{p['abs_path']}`")
    lines.append(f"- **GitHub URL**: {p['github_url']}")
    lines.append(f"- **Start Script**: `{'./start.sh' if p['has_start_script'] else 'N/A'}`")
    
    if p.get("is_running"):
        lines.append(f"- **Active Server Ports**: {json.dumps(p['running_ports'])}")
    else:
        lines.append(f"- **Detected Ports**: {p.get('detected_ports', [])}")
        
    if p.get("conversation_id"):
        lines.append(f"- **Previous Session Conversation ID**: `{p['conversation_id']}`")

    lines.append("\n---\n")

    # Read SKILL.md if present
    if p.get("skill_path") and os.path.exists(p["skill_path"]):
        lines.append("## 🛠️ SKILL Blueprint & Specifications")
        try:
            with open(p["skill_path"], "r") as f:
                lines.append(f.read())
        except Exception as e:
            lines.append(f"Error reading SKILL file: {e}")
        lines.append("\n---\n")

    # Read summary report if present
    if p.get("summary_file") and os.path.exists(p["summary_file"]):
        lines.append("## 📄 Session Executive Summary Report")
        try:
            with open(p["summary_file"], "r") as f:
                lines.append(f.read())
        except Exception as e:
            lines.append(f"Error reading summary file: {e}")

    return "\n".join(lines)
