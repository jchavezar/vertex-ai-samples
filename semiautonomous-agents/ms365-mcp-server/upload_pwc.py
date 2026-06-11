#!/usr/bin/env python3
"""
Orchestration script to upload the unzipped PwC directory to SharePoint.
Recreates the exact folder structure and uses chunked Upload Sessions for large files.
"""

import os
import sys
import logging

# Set up logging to show progress
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("upload_pwc")

# Add the current directory to python path so we can import tools and auth
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables before importing auth/graph
os.environ["MS365_CLIENT_ID"] = "44260445-702b-4d0c-aa37-cbed79b50531"
os.environ["MS365_TENANT_ID"] = "de46a3fd-0d68-4b25-8343-6eb5d71afce9"

from tools.sharepoint import create_folder, upload_local_file
from auth import get_auth_manager

# Target SharePoint drive ID for CWP Documents
DRIVE_ID = "b!xFcXid_TF062rl7B3zkH6TUM2tlkfTlJulj7lM9_273ba-ph-3SyQ4G-wGVnxfpz"
LOCAL_DIR = "/usr/local/google/home/jesusarguelles/Downloads/pwc_unzipped" if os.path.exists("/usr/local/google/home/jesusarguelles/Downloads/pwc_unzipped") else "/Users/jesusarguelles/Downloads/pwc_unzipped"


def ensure_sharepoint_folder(drive_id: str, rel_path: str, created_set: set):
    """
    Ensures that a relative folder path exists on SharePoint.
    rel_path example: 'Background Research/nested' or 'Client Work'
    """
    if not rel_path or rel_path == ".":
        return
    
    # Normalize path separators
    parts = [p for p in rel_path.replace("\\", "/").split("/") if p]
    
    current_path = ""
    for part in parts:
        parent_path = current_path if current_path else "/"
        current_path = f"{current_path}/{part}".strip("/")
        
        if current_path in created_set:
            continue
            
        logger.info(f"Ensuring folder '{part}' exists under '{parent_path}'...")
        res = create_folder(drive_id, parent_path, part)
        logger.info(f"Result: {res}")
        created_set.add(current_path)


def main():
    # Verify we are authenticated, or start device flow if not
    auth_manager = get_auth_manager()
    if not auth_manager.is_authenticated():
        logger.info("Not authenticated. Starting MSAL device code flow...")
        flow = auth_manager.start_device_code_flow()
        user_code = flow.get("user_code", "")
        verification_uri = flow.get("verification_uri", "https://microsoft.com/devicelogin")
        
        logger.info("\n" + "="*60)
        logger.info("MS365 AUTOMATED LOGIN REQUIRED")
        logger.info(f"Verification URL: {verification_uri}")
        logger.info(f"User Code: {user_code}")
        logger.info("="*60 + "\n")
        
        # This will block and poll until authenticated in the browser
        logger.info("Waiting for browser authentication to complete...")
        account = auth_manager.complete_device_code_flow(flow)
        logger.info(f"Successfully authenticated as: {account.get('username')} ({account.get('name')})")
    else:
        account = auth_manager.get_account_info()
        logger.info(f"Already authenticated as: {account.get('username')} ({account.get('name')})")
    
    if not os.path.exists(LOCAL_DIR):
        logger.error(f"Local source directory does not exist: {LOCAL_DIR}")
        sys.exit(1)
        
    logger.info(f"Starting recursive upload from local: {LOCAL_DIR}")
    
    created_folders = set()
    
    # Recursively walk the local directory structure
    for root, dirs, files in os.walk(LOCAL_DIR):
        # Calculate relative path from the root directory
        rel_root = os.path.relpath(root, LOCAL_DIR)
        
        if rel_root != ".":
            # Ensure this directory (and any parents) exists on SharePoint
            ensure_sharepoint_folder(DRIVE_ID, rel_root, created_folders)
            
        # Upload all files in the current folder
        for file_name in files:
            # Skip hidden/system files
            if file_name.startswith("._") or file_name == ".DS_Store":
                continue
                
            local_file_path = os.path.join(root, file_name)
            
            # Destination folder path on SharePoint
            # If rel_root is ".", it should be "/"
            dest_folder = "/" if rel_root == "." else f"/{rel_root}"
            
            logger.info(f"Uploading '{file_name}' to '{dest_folder}' ({os.path.getsize(local_file_path)} bytes)...")
            try:
                res = upload_local_file(DRIVE_ID, dest_folder, file_name, local_file_path)
                logger.info(f"Upload Result: {res}")
            except Exception as e:
                logger.error(f"Failed to upload '{file_name}': {e}")


if __name__ == "__main__":
    main()
