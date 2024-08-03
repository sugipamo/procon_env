import subprocess
import sys
import os


TEMPLATE = """"""

os.chdir(os.path.dirname(os.path.abspath(__file__)))
contest_name = sys.argv[1]
subprocess.check_output("cargo compete new " + contest_name, shell=True)
os.chdir(contest_name)

for a in os.listdir("./src/bin"):
    with open("./src/" + a.replace(".rs", ".py"), "w") as f:
        f.write(TEMPLATE)


