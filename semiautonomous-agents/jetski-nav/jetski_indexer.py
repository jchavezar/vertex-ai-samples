import os
import json
import re
import subprocess
from datetime import datetime

REPO_BASE = os.path.expanduser("~/IdeaProjects/vertex-ai-samples/semiautonomous-agents")
BRAIN_BASES = [
    ("jetski", os.path.expanduser("~/.gemini/jetski/brain")),
    ("antigravity-cli", os.path.expanduser("~/.gemini/antigravity-cli/brain")),
    ("antigravity-ide", os.path.expanduser("~/.gemini/antigravity-ide/brain")),
    ("antigravity", os.path.expanduser("~/.gemini/antigravity/brain")),
    ("antigravity-backup", os.path.expanduser("~/.gemini/antigravity-backup/brain")),
]
INDEX_OUTPUT = os.path.join(REPO_BASE, "jetski-nav", "PROJECT_INDEX.json")
CATALOG_OUTPUT = os.path.join(REPO_BASE, "CATALOG.md")

def get_active_ports():
    """Detects active listening ports and processes using lsof."""
    active_ports = {}
    try:
        cmd = "lsof -i -P -n | grep LISTEN"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        for line in res.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split()
            proc_name = parts[0]
            pid = parts[1]
            match = re.search(r":(\d+)\s+\(LISTEN\)", line)
            if match:
                port = int(match.group(1))
                active_ports[port] = {"process": proc_name, "pid": pid}
    except Exception as e:
        print(f"Error checking active ports: {e}")
    return active_ports

def scan_conversation_brains():
    """Scans ALL 5 brain directories across jetski, antigravity-cli, antigravity-ide, antigravity, and backup."""
    brain_map = {}

    for engine_name, brain_base in BRAIN_BASES:
        if not os.path.exists(brain_base):
            continue

        for conv_id in os.listdir(brain_base):
            conv_dir = os.path.join(brain_base, conv_id)
            if not os.path.isdir(conv_dir) or conv_id.startswith('.'):
                continue

            summaries = []
            project_hints = set()
            confidence = 0.85

            transcript_log = os.path.join(conv_dir, ".system_generated", "logs", "transcript.jsonl")
            if os.path.exists(transcript_log):
                try:
                    with open(transcript_log, "r", errors="ignore") as f:
                        content = f.read(65536)
                        matches = re.findall(r"semiautonomous-agents/([a-zA-Z0-9_\-]+)", content)
                        for m in matches:
                            project_hints.add(m)
                            confidence = 1.0
                except Exception:
                    pass

            for fname in os.listdir(conv_dir):
                fpath = os.path.join(conv_dir, fname)
                if fname.endswith(".md"):
                    summaries.append(fpath)
                elif fname == "scratch":
                    continue

                if os.path.isfile(fpath) and fname.endswith((".md", ".json", ".py")):
                    try:
                        with open(fpath, "r", errors="ignore") as f:
                            content = f.read(16384)
                            matches = re.findall(r"semiautonomous-agents/([a-zA-Z0-9_\-]+)", content)
                            for m in matches:
                                project_hints.add(m)
                                confidence = 1.0
                    except Exception:
                        pass

            brain_map[conv_id] = {
                "conversation_id": conv_id,
                "engine_name": engine_name,
                "transcript_log_path": transcript_log if os.path.exists(transcript_log) else None,
                "summaries": summaries,
                "project_hints": list(project_hints),
                "confidence_score": confidence,
                "last_modified": datetime.fromtimestamp(os.path.getmtime(conv_dir)).isoformat()
            }

    return brain_map

def scan_projects():
    """Scans all semiautonomous-agents directories and extracts deployment metadata with confidence scores."""
    if not os.path.exists(REPO_BASE):
        return []

    active_ports = get_active_ports()
    brain_map = scan_conversation_brains()

    projects = []
    
    for folder in sorted(os.listdir(REPO_BASE)):
        folder_path = os.path.join(REPO_BASE, folder)
        if not os.path.isdir(folder_path) or folder.startswith("."):
            continue

        readme_path = os.path.join(folder_path, "README.md")
        start_script = os.path.join(folder_path, "start.sh")
        
        skill_file = None
        skills_dir = os.path.join(folder_path, "skills")
        if os.path.exists(skills_dir):
            for root, dirs, files in os.walk(skills_dir):
                for f in files:
                    if f.endswith(".md"):
                        skill_file = os.path.join(root, f)
                        break

        title = folder.replace("-", " ").replace("_", " ").title()
        description = "Autonomous Agent Deployment"
        if os.path.exists(readme_path):
            try:
                with open(readme_path, "r", errors="ignore") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                    if lines and lines[0].startswith("#"):
                        title = lines[0].lstrip("#").strip()
                    for l in lines[1:]:
                        if l and not l.startswith("#") and not l.startswith("!"):
                            description = l
                            break
            except Exception:
                pass

        detected_ports = []
        for check_file in ["README.md", "start.sh", "backend/main.py", "frontend/vite.config.js"]:
            fp = os.path.join(folder_path, check_file)
            if os.path.exists(fp):
                try:
                    with open(fp, "r", errors="ignore") as f:
                        text = f.read()
                        ports = re.findall(r"\b(port\s*[:=]?\s*|:\s*)(\d{4})\b", text, re.IGNORECASE)
                        for _, p in ports:
                            p_int = int(p)
                            if 1024 <= p_int <= 65535 and p_int not in detected_ports:
                                detected_ports.append(p_int)
                except Exception:
                    pass

        running_ports = {}
        for p in detected_ports:
            if p in active_ports:
                running_ports[p] = active_ports[p]

        matched_conv = None
        matched_summary = None
        matched_engine = "jetski"
        matched_tlog = None
        match_confidence = 0.0

        for cid, binfo in brain_map.items():
            if folder in binfo["project_hints"]:
                matched_conv = cid
                matched_engine = binfo["engine_name"]
                matched_tlog = binfo["transcript_log_path"]
                match_confidence = binfo["confidence_score"]
                if binfo["summaries"]:
                    matched_summary = binfo["summaries"][0]
                break

        rel_path = os.path.relpath(folder_path, os.path.dirname(REPO_BASE))

        project_meta = {
            "id": folder,
            "title": title,
            "description": description,
            "path": rel_path,
            "abs_path": folder_path,
            "has_start_script": os.path.exists(start_script),
            "has_skill": skill_file is not None,
            "skill_path": skill_file,
            "detected_ports": detected_ports,
            "running_ports": running_ports,
            "is_running": len(running_ports) > 0,
            "conversation_id": matched_conv,
            "brain_engine": matched_engine,
            "transcript_log_path": matched_tlog,
            "confidence_score": match_confidence,
            "summary_file": matched_summary,
            "github_url": f"https://github.com/jchavezar/vertex-ai-samples/tree/main/{rel_path}"
        }
        projects.append(project_meta)

    return projects

def generate_index():
    projects = scan_projects()
    index_data = {
        "generated_at": datetime.now().isoformat(),
        "total_projects": len(projects),
        "running_projects": len([p for p in projects if p["is_running"]]),
        "projects": projects
    }

    os.makedirs(os.path.dirname(INDEX_OUTPUT), exist_ok=True)
    with open(INDEX_OUTPUT, "w") as f:
        json.dump(index_data, f, indent=2)

    print(f"✅ Generated {INDEX_OUTPUT} with {len(projects)} projects ({index_data['running_projects']} active)")
    return index_data

if __name__ == "__main__":
    generate_index()
