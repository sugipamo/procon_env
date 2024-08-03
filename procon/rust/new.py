import subprocess
import sys
import os

TEMPLATE = """"""

contest_name = sys.argv[1]
os.chdir(os.path.dirname(os.path.abspath(__file__)))

subprocess.check_output("cargo compete new " + contest_name, shell=True)

import json
if os.path.exists("./../.vscode/settings.json"):
    with open("./../.vscode/settings.json", mode="r") as f:
        j = json.load(f)
else:
    j = {"rust-analyzer.linkedProjects":[]}
j["rust-analyzer.linkedProjects"].append(f"./rust/{contest_name}/Cargo.toml")
j["rust-analyzer.linkedProjects"] = list(set(j["rust-analyzer.linkedProjects"]))
    
with open("./../.vscode/settings.json", "w") as f:
    f.write(json.dumps(j))

