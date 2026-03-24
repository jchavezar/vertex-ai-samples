import os
import re

TARGET_DIR = "/usr/local/google/home/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity"

SENSITIVE_PATTERNS = [
    re.compile(r'(?i)password\s*=\s*[\'"][^\'"]+[\'"]'),
    re.compile(r'(?i)secret\s*=\s*[\'"][^\'"]+[\'"]'),
    re.compile(r'(?i)api_key\s*=\s*[\'"][^\'"]+[\'"]'),
    re.compile(r'(?i)token\s*=\s*[\'"][^\'"]+[\'"]'),
    re.compile(r'sk-[A-Za-z0-9_-]{48}'),
    re.compile(r'ya29\.[a-zA-Z0-9_-]+'),
    re.compile(r'(?i)bearer\s+[\w\-.]+'),
    re.compile(r'(?i)client_secret\s*[:=]\s*[\'"][^\'"]+[\'"]')
]

# Exclude list 
IGNORE_DIRS = [".git", "__pycache__", "node_modules", "dist", "build", ".venv", "venv"]

findings = []

for root, dirs, files in os.walk(TARGET_DIR):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    for file in files:
        if file.endswith(('.py', '.json', '.txt', '.js', '.ts', '.env', '.yaml', '.yml', '.env.example')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines):
                        for pattern in SENSITIVE_PATTERNS:
                            if pattern.search(line):
                                findings.append(f"{filepath}:{idx + 1} -> {line.strip()}")
            except Exception:
                pass

with open(f"{TARGET_DIR}/security_audit_results.log", "w") as out:
    if findings:
        for f in findings:
            out.write(f + "\n")
    else:
        out.write("No hardcoded secrets found.\n")

print(f"Audit complete. Found {len(findings)} potential secrets.")
