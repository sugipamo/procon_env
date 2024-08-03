import subprocess
import sys
import os
import webbrowser

AHCTOOLSDIR = "tools"

USAGE  ="""
# usage: 
# python manage.py abc301 new
# python manage.py abc301 open a
# python manage.py abc301 python test a
# python manage.py ahc024 python test
"""

# 一番上のインタプリタがデフォルトになる
INTERPRETER = {
    "python": "python", 
    "rust": "rust",
    "py": "python",
    "rs": "rust",
}

EXTENSIONS = {
    "python": "py", 
    "rust": "rs",
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

argv = sys.argv
if len(argv) < 3:
    print("invalid argument")
    print(USAGE)
    exit()

contest_name = sys.argv[1]
argv = sys.argv[2:]

interpreter = ""

def new(*args):
    import shutil
    for i in set(INTERPRETER.values()):
        if os.path.exists(f"{i}/{contest_name}"):
            shutil.rmtree(f"{i}/{contest_name}", ignore_errors=True)
        subprocess.call(f"python {i}/new.py {contest_name}", shell=True)

    if "ahc" in contest_name:
        url =  "https://atcoder.jp/contests/" + contest_name + "/tasks/" + contest_name + "_a"
        
        from lxml import html
        import requests
        response = requests.get(url)
        lxml_data = html.fromstring(response.content)
        temp = lxml_data.xpath('.//a[contains(text(),"ローカル")]')
        
        shutil.rmtree("tools.zip", ignore_errors=True)
        if temp:
            url = temp[0].get('href')
            tools = requests.get(url)
            with open('tools.zip', 'wb') as f:
                f.write(tools.content)
        else:
            input("download tools.zip from " + url + " and press Enter")
        
        for i in set(INTERPRETER.values()):
            shutil.unpack_archive("tools.zip", f"{i}/{contest_name}")


def open_task(*args):
    #[0] = taskname
    taskname = args[0]
    path = list(INTERPRETER.values())[0] if not interpreter else interpreter
    if not os.path.exists(f"{path}/{contest_name}"):
        raise Exception("it needs to create new task")

    def helper(interpreter):
        src = "src"
        if interpreter == "rust":
            src = "src/bin"
        ext = EXTENSIONS[interpreter]
        subprocess.call(f"code ./{interpreter}/{contest_name}/{src}/{taskname}.{ext}", shell=True)
    
    if interpreter == "":
        for i in set(INTERPRETER.values()):
            helper(i)
    else:
        helper(interpreter)

    if interpreter == "rust":
        with open("./.vscode/settings.json", "w") as f:
            import json
            f.write(json.dumps({"rust-analyzer.linkedProjects": [f"./rust/{contest_name}/Cargo.toml"]}))

        
    url = "https://atcoder.jp/contests/" + contest_name + "/tasks/" + contest_name + "_" + taskname
    webbrowser.open(url)

def make_samples(*args):
    #[0] = taskname
    #[1] = n
    taskname = args[0]
    n = int(args[1])
    workdir = os.path.dirname(os.path.abspath(__file__))
    workdir = os.path.join(workdir, interpreter, contest_name)
    sys.path.append(AHCTOOLSDIR)
    make_sample = __import__("make_sample")
    make_sample.delete_samples(workdir, taskname)
    make_sample.make_samples(workdir, taskname, n)

def ahctest(*args):
    #[0] = cnt
    cnt = args[0]
    workdir = os.path.dirname(os.path.abspath(__file__))
    workdir = os.path.join(workdir, interpreter, contest_name)
    subprocess.call(f"python {AHCTOOLSDIR}/ahc_tester.py {workdir} {cnt}", shell=True)
    

def test(*args):
    #[0] = taskname
    taskname = args[0]
    subprocess.call(f"cd {interpreter}/{contest_name}\ncargo compete test " + taskname, shell=True)

def submit(*args):
    #[0] = taskname
    taskname = args[0]
    if interpreter == "":
        raise Exception("it needs interpreter name")
    else:
        if "ahc" in contest_name:
            subprocess.call(f"cd {interpreter}/{contest_name}\ncargo compete submit " + taskname + " --no-test", shell=True)
        else:
            subprocess.call(f"cd {interpreter}/{contest_name}\ncargo compete submit " + taskname, shell=True)

for k in INTERPRETER:
    if k in argv:
        interpreter = INTERPRETER[k]
        break

if interpreter == "":
    interpreter = list(INTERPRETER.values())[0]

COMMANDS = {
    "new": (new, 0),
    "n": (new, 0),
    "test": (test, 1),
    "t": (test, 1),
    "ahctest": (ahctest, 1),
    "ahct": (ahctest, 1),
    "ahc": (ahctest, 1),
    "submit": (submit, 1),
    "s": (submit, 1),
    "open": (open_task, 1),
    "o": (open_task, 1),
    "make_samples": (make_samples, 2),
    "mk": (make_samples, 2),
    "m": (make_samples, 2),
}

i = 0
while i < len(argv):
    if argv[i] in COMMANDS:
        command, n = COMMANDS[argv[i]]
        args = []
        for j in range(n):
            if i + j + 1 >= len(argv):
                raise Exception("invalid argument")
            args.append(argv[i + j + 1])
        i += n
        command(*args)
    i += 1      


