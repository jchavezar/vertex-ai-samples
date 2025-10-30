## ⚡ Getting Started (Quick Setup)

This guide uses **uv** for fast and reproducible environment setup and dependency management.

### Prerequisites

You need **Git** and the **uv** tool installed on your system.

*   **Install uv:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

### 1. Clone the Project

Get the latest version of the code from the repository:

```bash
git clone https://github.com/jchavezar/vertex-ai-samples.git
cd vertex-ai-samples/gen_ai/adk/
```

### 2. Setup the Environment

Use uv to create a dedicated virtual environment named .venv and then activate it.

```bash
# Create the virtual environment
uv venv

# Activate the environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Use the uv pip sync command to install all packages listed in requirements.txt. This step ensures your environment is an exact match for the defined dependencies by installing missing packages and uninstalling extras.

```bash
uv pip sync requirements.txt
```

### 4. Run the Application

You are now ready to run the project byt following this sequence.

#### Test
- [agent.py](agent.py): Is the ADK (Agent Development Kit) definition, for quick prototyping use:

```bash
adk web
```

#### Develop
- [deploy_agent_engine.py](deploy_agent_engine.py): Is an inline script `#%%` for IDEs like vscode or intellij, to run
parts of the script one by one.

Once the Agent Engine is developed, save the resource_name and use it in the next file:
([publish_to_ge.py](publish_to_ge.py))

e.g.
```python
"projects/254356041555/locations/us-central1/reasoningEngines/4066033581934247936"
```


#### Publish
-(push) [publish_to_ge.py](publish_to_ge.py): Is an inline script `#%%` to publish Agent Engine to Gemini Enterprise.

#### Test

From now go to Gemini Enterprise and find the new agent.



## 💡 Key `uv` Commands

| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Install** | `uv pip install <package>` | Install a new package. |
| **Sync** | `uv pip sync requirements.txt` | Ensure environment exactly matches the file. |
| **Upgrade** | `uv pip install --upgrade <package>` | Upgrade a specific package. |
| **Deactivate** | `deactivate` | Exit the virtual environment. |

---

## 🤝 Contributing

Contributions are welcome! Please see the [`CONTRIBUTING.md`](CONTRIBUTING.md) file for details.

## 📄 License

This project is licensed under the **[MIT License](LICENSE)** - see the `LICENSE` file for details.

