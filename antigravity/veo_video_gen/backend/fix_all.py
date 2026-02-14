import re

# Fix main.py
with open("main.py", "r") as f:
    main_code = f.read()

main_code = main_code.replace('from agent import video_expert_agent', 'from agent_pkg.agent import video_expert_agent')
main_code = main_code.replace('import agent', 'import agent_pkg.agent as agent')
main_code = main_code.replace('importlib.reload(agent)', 'importlib.reload(agent.agent)')
main_code = main_code.replace('"agent.py"', '"agent_pkg/agent.py"')
main_code = main_code.replace('["agent.py"]', '["agent_pkg"]')
main_code = main_code.replace('os.path.join(base_dir, "agent.py")', 'os.path.join(base_dir, "agent_pkg")')
main_code = main_code.replace('os.path.join(os.path.dirname(__file__), "agent_pkg")', 'os.path.join(os.path.dirname(__file__), "agent_pkg", "agent.py")')

with open("main.py", "w") as f:
    f.write(main_code)

# Fix test_deploy.py
with open("test_deploy.py", "r") as f:
    td_code = f.read()

td_code = td_code.replace('from agent import video_expert_agent', 'from agent_pkg.agent import video_expert_agent')
td_code = td_code.replace('os.path.join(base_dir, "agent.py")', 'os.path.join(base_dir, "agent_pkg")')

with open("test_deploy.py", "w") as f:
    f.write(td_code)
