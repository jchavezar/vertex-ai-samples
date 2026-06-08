#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Setup and replication script for the Gemini Enterprise MCP Co-work Portal recipe.
Copies application files, configures environment variables, and installs dependencies.
"""
import os
import sys
import shutil
import argparse
import subprocess
import json

# Setup configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPE_DIR = os.path.dirname(SCRIPT_DIR)
TEMPLATE_APP_DIR = os.path.join(RECIPE_DIR, "app")
RESOURCES_FILE = os.path.join(RECIPE_DIR, "last_setup_resources.json")

def get_default_project_id():
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=False
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "vtxdemos"

def get_default_project_number(project_id):
    try:
        res = subprocess.run(
            ["gcloud", "projects", "describe", project_id, "--format=value(projectNumber)"],
            capture_output=True,
            text=True,
            check=False
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "254356041555"

def parse_args():
    parser = argparse.ArgumentParser(description="Replicate and configure the GE MCP Co-work Portal.")
    parser.add_argument("--destination", help="Target path to replicate the application to.")
    parser.add_argument("--project-id", help="Google Cloud Project ID.")
    parser.add_argument("--project-number", help="Google Cloud Project Number.")
    parser.add_argument("--engine-id", help="Gemini Enterprise Engine ID.")
    parser.add_argument("--jira-url", help="Jira Site URL (e.g., sockcop.atlassian.net).")
    parser.add_argument("--sharepoint-url", help="SharePoint Site URL.")
    parser.add_argument("--non-interactive", action="store_true", help="Run without stdin prompts.")
    return parser.parse_args()

def main():
    print("==================================================")
    print(" GE MCP Co-work Portal Setup & Replication")
    print("==================================================")

    args = parse_args()

    # Determine interactive vs CLI mode
    is_interactive = not args.non_interactive

    # 1. Resolve Destination Path
    destination = args.destination
    if not destination:
        default_dest = "./ge-mcp-cowork-portal"
        if is_interactive:
            inp = input(f"Enter target replication folder [{default_dest}]: ").strip()
            destination = inp if inp else default_dest
        else:
            destination = default_dest
    destination = os.path.abspath(destination)

    # 2. Resolve Project ID
    project_id = args.project_id
    if not project_id:
        default_proj = get_default_project_id()
        if is_interactive:
            inp = input(f"Enter GCP Project ID [{default_proj}]: ").strip()
            project_id = inp if inp else default_proj
        else:
            project_id = default_proj

    # 3. Resolve Project Number
    project_number = args.project_number
    if not project_number:
        default_num = get_default_project_number(project_id)
        if is_interactive:
            inp = input(f"Enter GCP Project Number [{default_num}]: ").strip()
            project_number = inp if inp else default_num
        else:
            project_number = default_num

    # 4. Resolve Engine ID
    engine_id = args.engine_id
    if not engine_id:
        default_eng = "jira-testing_1778158449701"
        if is_interactive:
            inp = input(f"Enter Gemini Engine ID [{default_eng}]: ").strip()
            engine_id = inp if inp else default_eng
        else:
            engine_id = default_eng

    # 5. Resolve Jira Site URL
    jira_url = args.jira_url
    if not jira_url:
        default_jira = "sockcop.atlassian.net"
        if is_interactive:
            inp = input(f"Enter Jira site URL [{default_jira}]: ").strip()
            jira_url = inp if inp else default_jira
        else:
            jira_url = default_jira

    # 6. Resolve SharePoint Site URL
    sharepoint_url = args.sharepoint_url
    if not sharepoint_url:
        default_sp = ""
        if is_interactive:
            inp = input("Enter SharePoint site URL (optional): ").strip()
            sharepoint_url = inp if inp else default_sp
        else:
            sharepoint_url = default_sp

    print("\n[*] Configuration Summary:")
    print(f"  - Target Folder:   {destination}")
    print(f"  - GCP Project:     {project_id}")
    print(f"  - Project Number:  {project_number}")
    print(f"  - Engine ID:       {engine_id}")
    print(f"  - Jira Site URL:   {jira_url}")
    print(f"  - SharePoint URL:  {sharepoint_url if sharepoint_url else 'None'}")

    if is_interactive:
        confirm = input("\nDo you want to proceed with replication? [Y/n]: ").strip().lower()
        if confirm not in ("", "y", "yes"):
            print("[-] Cancelled by user.")
            sys.exit(0)

    # 7. Perform Copy Operations
    print(f"\n[*] Copying application template files to {destination}...")
    if os.path.exists(destination):
        print(f"[!] Target directory {destination} already exists.")
        if is_interactive:
            overwrite = input("Do you want to overwrite it? [y/N]: ").strip().lower()
            if overwrite not in ("y", "yes"):
                print("[-] Aborted to prevent data loss.")
                sys.exit(1)
        shutil.rmtree(destination)

    try:
        shutil.copytree(TEMPLATE_APP_DIR, destination)
        print("[+] Application files copied successfully.")
        
        # Copy .agent workflows and skills to target workspace .agent folder
        recipe_agent_dir = os.path.join(RECIPE_DIR, ".agent")
        dest_agent_dir = os.path.join(destination, ".agent")
        if os.path.exists(recipe_agent_dir):
            print("[*] Copying Antigravity skills and workflows into target .agent folder...")
            shutil.copytree(recipe_agent_dir, dest_agent_dir, dirs_exist_ok=True)
            print("[+] Antigravity workflows registered successfully in clone.")
    except Exception as e:
        print(f"[!] File copy failed: {e}")
        sys.exit(1)

    # 8. Create `.env` file in destination path
    print("[*] Creating .env file in target workspace...")
    env_content = f"""# Core Gemini Enterprise Grounding configurations
GOOGLE_CLOUD_PROJECT={project_id}
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-2.5-flash

# Set to true to route chat queries to Vertex Reasoning Engine Agent ID
USE_REASONING_ENGINE=True
REASONING_ENGINE_ID={engine_id}

# Connection defaults (Optional presets)
JIRA_DEFAULT_SITE={jira_url}
SHAREPOINT_DEFAULT_SITE={sharepoint_url}
"""
    try:
        with open(os.path.join(destination, ".env"), "w") as f:
            f.write(env_content)
        # Also copy example env to backend
        backend_env_example = os.path.join(destination, "backend", ".env.example")
        backend_env = os.path.join(destination, "backend", ".env")
        if os.path.exists(backend_env_example):
            shutil.copyfile(backend_env_example, backend_env)
        print("[+] Environment configuration files generated.")
    except Exception as e:
        print(f"[!] Failed to create .env configuration: {e}")
        sys.exit(1)

    # 9. Install NPM Dependencies
    print("[*] Installing React frontend node modules...")
    frontend_dir = os.path.join(destination, "frontend")
    try:
        subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        print("[+] Frontend node modules installed.")
    except Exception as e:
        print(f"[!] Warning: 'npm install' failed or npm not found: {e}. You may need to run it manually.")

    # 10. Save replication details to resources tracking JSON
    resources_data = {
        "destination_path": destination,
        "gcp_project": project_id,
        "engine_id": engine_id
    }
    try:
        with open(RESOURCES_FILE, "w") as f:
            json.dump(resources_data, f, indent=2)
        print("[+] Saved deployment resources tracking info.")
    except Exception as e:
        print(f"[!] Warning: Failed to write last_setup_resources.json: {e}")

    print("\n==================================================")
    print(" 🎉 Setup and Replication Complete!")
    print("==================================================")
    print(f"  1. Go to your replicated folder: {destination}")
    print("  2. Run the startup script:")
    print("     $ ./start.sh")
    print("==================================================\n")

if __name__ == "__main__":
    main()
