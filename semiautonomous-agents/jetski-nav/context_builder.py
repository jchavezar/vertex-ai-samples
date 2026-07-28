import os
import json
import subprocess

def get_git_commit_history(abs_path):
    """Fetches recent git commit history for a project folder."""
    try:
        cmd = f"git log -n 8 --oneline -- {abs_path}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=abs_path)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def inspect_directory_files(abs_path):
    """Summarizes directory structure and entrypoint configuration files."""
    summary_parts = []
    if not os.path.exists(abs_path):
        return ""

    try:
        items = sorted(os.listdir(abs_path))
        key_files = [i for i in items if not i.startswith(".") and i != "node_modules" and i != "__pycache__"]
        summary_parts.append(f"**Directory Contents**: `{', '.join(key_files[:15])}`")
    except Exception:
        pass

    # Read package.json if present
    pkg_path = os.path.join(abs_path, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, "r") as f:
                data = json.load(f)
                name = data.get("name", "")
                scripts = list(data.get("scripts", {}).keys())
                deps = list(data.get("dependencies", {}).keys()) + list(data.get("devDependencies", {}).keys())
                summary_parts.append(f"**NPM Package**: `{name}` | **Scripts**: `{', '.join(scripts[:5])}` | **Dependencies**: `{', '.join(deps[:8])}`")
        except Exception:
            pass

    # Read requirements.txt if present
    req_path = os.path.join(abs_path, "requirements.txt")
    if os.path.exists(req_path):
        try:
            with open(req_path, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
                summary_parts.append(f"**Python Dependencies**: `{', '.join(lines[:10])}`")
        except Exception:
            pass

    return "\n".join(summary_parts)

def build_context_bundle(p):
    """Builds a rich, comprehensive context prompt for an AI agent turn."""
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
        cid = p['conversation_id']
        tpath = p.get('transcript_log_path', f"~/.gemini/jetski/brain/{cid}/.system_generated/logs/transcript.jsonl")
        lines.append(f"- **Previous Session Conversation ID**: `{cid}`")
        lines.append(f"- **Brain Tool Engine**: `{p.get('brain_engine', 'jetski')}`")
        lines.append(f"- **Brain Transcript Log Path**: `{tpath}`")
        lines.append(f"- **Agent Instruction**: *Read the transcript log path above if you need step-by-step history from previous sessions.*")

    lines.append("\n---\n")

    # Include SKILL.md if present
    if p.get("skill_path") and os.path.exists(p["skill_path"]):
        lines.append("## 🛠️ SKILL Blueprint & Specifications")
        try:
            with open(p["skill_path"], "r") as f:
                lines.append(f.read())
        except Exception as e:
            lines.append(f"Error reading SKILL file: {e}")
        lines.append("\n---\n")

    # Include Session Executive Summary Report if present
    if p.get("summary_file") and os.path.exists(p["summary_file"]):
        lines.append("## 📄 Session Executive Summary Report")
        try:
            with open(p["summary_file"], "r") as f:
                lines.append(f.read())
        except Exception as e:
            lines.append(f"Error reading summary file: {e}")
        lines.append("\n---\n")

    # Directory Structure & Configuration Summary
    dir_info = inspect_directory_files(p['abs_path'])
    if dir_info:
        lines.append("## 📦 Codebase Structure & Configuration")
        lines.append(dir_info)
        lines.append("\n---\n")

    # README.md
    readme_path = os.path.join(p['abs_path'], "README.md")
    if os.path.exists(readme_path):
        lines.append("## 📄 Project Documentation (README)")
        try:
            with open(readme_path, "r", errors="ignore") as f:
                readme_lines = f.readlines()
                lines.append("```markdown")
                lines.append("".join(readme_lines[:50]))
                lines.append("```\n")
        except Exception:
            pass

    # Git Commit Log History
    commits = get_git_commit_history(p['abs_path'])
    if commits:
        lines.append("## 📜 Recent Git Commit History")
        lines.append("```text")
        lines.append(commits)
        lines.append("```\n")

    return "\n".join(lines)
