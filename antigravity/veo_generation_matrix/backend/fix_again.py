with open("test_deploy.py", "r") as f:
    code = f.read()

new_code = code.replace("==1.104.0", "")
new_code = new_code.replace("==1.7.0", "")
new_code = new_code.replace("==1.26.0", "")

with open("test_deploy.py", "w") as f:
    f.write(new_code)
