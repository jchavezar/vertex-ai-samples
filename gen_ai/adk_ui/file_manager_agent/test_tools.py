import sys
import os

# Add the current directory to sys.path so we can import the tools
sys.path.append(os.getcwd())

from tools.gcs_file_manager import list_files, find_file

print("Testing list_files...")
res = list_files(bucket_name="vtxdemos-datasets-public", prefix="8k-10q-files-q3-2025/")
print(f"Result type: {type(res)}")
print(f"Result: {res}")

print("\nTesting find_file...")
res_find = find_file(bucket_name="vtxdemos-datasets-public", file_name_substring=".pdf", prefix="8k-10q-files-q3-2025/")
print(f"Result type: {type(res_find)}")
print(f"Result: {res_find}")
