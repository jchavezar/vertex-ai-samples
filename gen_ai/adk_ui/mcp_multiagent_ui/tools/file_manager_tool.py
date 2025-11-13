# tools/file_manager_tool.py
import os
from typing import List, Dict, Union

def list_local_files(path: str = ".") -> List[Dict[str, Union[str, bool, int]]]:
  """Lists files and directories in a given local path.

  Args:
    path: The directory path to list. Defaults to the current directory.

  Returns:
    A list of dictionaries, where each dictionary represents a file or directory
    with its name, type (file/directory), and size (for files).
  """
  results = []
  try:
    with os.scandir(path) as entries:
      for entry in entries:
        info = {
            "name": entry.name,
            "is_directory": entry.is_dir(),
            "is_file": entry.is_file(),
            "path": os.path.join(path, entry.name)
        }
        if entry.is_file():
          info["size_bytes"] = entry.stat().st_size
        results.append(info)
  except FileNotFoundError:
    return [{"error": f"Path not found: {path}"}]
  except Exception as e:
    return [{"error": f"An error occurred: {e}"}]
  return results

def create_local_file(file_path: str, content: str = "") -> Dict[str, str]:
  """Creates a local file with the specified content.

  Args:
    file_path: The full path to the file to create.
    content: The content to write to the file. Defaults to an empty string.

  Returns:
    A dictionary indicating success or failure.
  """
  try:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
      f.write(content)
    return {"status": "success", "message": f"File '{file_path}' created successfully."}
  except Exception as e:
    return {"status": "error", "message": f"Failed to create file '{file_path}': {e}"}
