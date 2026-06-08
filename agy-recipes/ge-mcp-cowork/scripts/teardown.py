#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Teardown script for the Gemini Enterprise MCP Co-work Portal recipe.
Deletes the replicated application folder and cleans up resources metadata.
"""
import os
import shutil
import json

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPE_DIR = os.path.dirname(SCRIPT_DIR)
RESOURCES_FILE = os.path.join(RECIPE_DIR, "last_setup_resources.json")

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Tear down the replicated GE MCP Co-work Portal.")
    parser.add_argument("--non-interactive", action="store_true", help="Run without confirmation prompts.")
    return parser.parse_args()

def main():
    print("==================================================")
    print(" GE MCP Co-work Portal Teardown & Cleanup")
    print("==================================================")

    args = parse_args()
    is_interactive = not args.non_interactive

    if not os.path.exists(RESOURCES_FILE):
        print("[!] No setup resources tracking file found. Nothing to tear down.")
        return

    try:
        with open(RESOURCES_FILE) as f:
            data = json.load(f)
    except Exception as e:
        print(f"[!] Failed to parse setup resources file: {e}")
        return

    destination = data.get("destination_path")
    if not destination:
        print("[!] No destination path tracked in resources file.")
        return

    print(f"[*] Target directory to remove: {destination}")
    
    if os.path.exists(destination):
        confirm = "y"
        if is_interactive:
            confirm = input(f"Are you sure you want to permanently delete the folder {destination}? [y/N]: ").strip().lower()
        
        if confirm in ("y", "yes"):
            try:
                shutil.rmtree(destination)
                print(f"[+] Folder deleted successfully: {destination}")
            except Exception as e:
                print(f"[!] Failed to delete directory: {e}")
        else:
            print("[-] Cancelled by user. Folder was not deleted.")
    else:
        print(f"[!] Replicated folder does not exist at {destination} (already removed).")

    # Clean up resources file
    try:
        os.remove(RESOURCES_FILE)
        print("[+] Cleaned up last_setup_resources.json.")
    except Exception as e:
        print(f"[!] Failed to remove resources tracking file: {e}")

    print("\n[+] Teardown complete!\n")

if __name__ == "__main__":
    main()
