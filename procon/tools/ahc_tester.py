
import datetime
import subprocess
import multiprocessing
import os
import ahc_analyzer
import time
import sys

INTXTCOUNT = 10
POOLCOUNT = 10

if len(sys.argv) < 2:
    print("invalid argument")
    print("python ahc_tester.py [workdir] [intxtcount]")
    exit()

workdir = sys.argv[1]
workdir = os.path.abspath(workdir)

if len(sys.argv) > 2:
    INTXTCOUNT = int(sys.argv[2])


def make_anime(inpath, outpath, otherpath=None):
    ANIMEKEYWORD = "#anime"
    shapes = {}
    now = 0
    timeunit = 0.1
    gridunit = 10.0
    xmax = 0
    ymax = 0

    def make_shape(animate="", args={}):
        shapename = args.pop("shapename")
        args.pop("time")
        transform = args.pop("transform")
        if shapename == "circle":
            args["cx"] = transform[1] + args["width"] / 2
            args["cy"] = transform[0] + args["height"] / 2
            args["r"] = args["width"] / 2
        else:
            args["x"] = transform[1]
            args["y"] = transform[0]
        command = " ".join(
            [f'{k}="{args[k]}"' for k in args])

        if animate:
            animate = "\n" + animate + "\n"
            return f"""<{shapename} {command}>{animate}</{shapename}>"""
        else:
            return f"""<{shapename} {command}/>"""

    with open(inpath, "r") as f:
        intxt = f.read()

    preargs = {}
    settingblock = False

    for line in intxt.split("\n"):
        addcnt = False
        if not line.startswith(ANIMEKEYWORD):
            continue
        for line in line.split(ANIMEKEYWORD):
            line = line.split()
            if not line:
                continue
            if line[0] == "timeunit":
                if settingblock:
                    continue
                timeunit = float(line[1])
                continue

            if line[0] == "gridunit":
                if settingblock:
                    continue
                gridunit = float(line[1])
                continue

            addcnt = True
            settingblock = True
            args = {
                "id": (str, "default"),
                "y": (int, 0),
                "x": (int, 0),
                "a": (float, 1.0),
                "r": (float, 1.0),
                "g": (float, 1.0),
                "b": (float, 1.0),
                "shapename": (str, "rect"),
                "width": (float, gridunit),
                "height": (float, gridunit),
                "time": (0, 0),
            }

            for i, a in enumerate(args):
                if i < len(line):
                    args[a] = args[a][0](line[i])
                else:
                    if args["id"] in preargs:
                        args[a] = preargs[args["id"]][a]
                    else:
                        args[a] = args[a][1]

            preargs[args["id"]] = args

            def tohex(num):
                return hex(int(num * 255))[2:].zfill(2)

            shapes.setdefault(args["id"], [])
            shapes[args["id"]].append({
                "shapename": args["shapename"],
                "transform": (args["y"] * gridunit, args["x"] * gridunit),
                "width": gridunit,
                "height": gridunit,
                "fill": "#" + tohex(args["r"]) + tohex(args["g"]) + tohex(args["b"]),
                "fill-opacity": args["a"],
                "time": now * timeunit,
            })
            xmax = max(xmax, args["x"] * gridunit + args["width"] * gridunit)
            ymax = max(ymax, args["y"] * gridunit + args["height"] * gridunit)
        if addcnt:
            now += 1

    outputs = []
    for id in shapes:
        shape = shapes[id][0]
        if shape["time"] != 0.0:
            shape["fill-opacity"] = 0.0
        shape = [shape] + shapes[id]

        change = []
        for name in shape[0]:
            if name == "id" or name == "time":
                continue
            startpos = shape[0][name]
            for i in range(1, len(shape)):
                time_ = shape[i]["time"]
                now, pre = shape[i][name], shape[i - 1][name]
                if now == pre:
                    continue

                if type(now) == tuple:

                    now = ",".join([str(j - i)
                                   for i, j in zip(startpos, now)][::-1])
                    pre = ",".join([str(j - i)
                                   for i, j in zip(startpos, pre)][::-1])

                command = '<{tagname} attributeName="{name}" values="{values}" begin ="{begin}s" dur="{timeunit}s" fill="freeze"/>'.format(
                    tagname="animate" if name != "transform" else "animateTransform",
                    name=name,
                    values=f"{pre};{now}",
                    begin=time_,
                    timeunit=timeunit
                )
                change.append(command)

        outputs.append(make_shape("\n".join(change), shapes[id][0]))

    with open(outpath, "w") as f:
        print(
            f'<svg/>\n<svg xmlns="http://www.w3.org/2000/svg" width="{xmax}" height="{ymax}">', file=f)
        print("\n".join(outputs), file=f)
        print("</svg>", file=f)

    if otherpath:
        with open(inpath, "w") as f:
            for t in intxt.split("\n"):
                if t.startswith(ANIMEKEYWORD):
                    continue
                print(t, file=f)
        with open(otherpath, "a") as f:
            print("\n", file=f)
            for t in intxt.split("\n"):
                if t.startswith(ANIMEKEYWORD):
                    print(t, file=f)


rusttoolsmode = os.path.exists(os.path.join(workdir, "tools", "Cargo.lock"))

os.chdir(workdir + "/tools")
is_interactive = os.path.exists("./src/bin/tester.rs")
if len(os.listdir("./in")) != INTXTCOUNT and rusttoolsmode:
    subprocess.call("rm -rf in\nmkdir in", shell=True)
    with open("seeds.txt", "w") as f:
        [f.write(str(i) + "\n") for i in range(INTXTCOUNT)]
    subprocess.call("cargo run --release --bin gen seeds.txt", shell=True)


os.chdir(workdir)
historyfolder = os.path.abspath("./history/temp")
rootfolder = workdir
interpreter = [i for i in ["rust", "python"] if i in rootfolder][0]


subprocess.call("mkdir -p history\nmkdir -p history/temp", shell=True)
if rusttoolsmode:
    subprocess.call(
        f"cp ./tools/seeds.txt {historyfolder}/seeds.txt", shell=True)
    subprocess.call("cd tools\ncargo build --release --bin vis", shell=True)
if is_interactive:
    subprocess.call("cd tools\ncargo build --release --bin tester", shell=True)

for path in ["in", "out", "err", "others", "vis", "anime"]:
    subprocess.call(f"rm -rf {historyfolder}/{path}", shell=True)
    subprocess.call(f"mkdir -p {historyfolder}/{path}", shell=True)


if interpreter == "rust":
    binname = workdir.split("/")[-1] + "-a"
    subprocess.call(f"cargo build --release --bin {binname}", shell=True)
    subprocess.call(f"cp ./src/bin/a.rs {historyfolder}/a.rs", shell=True)
    bootcommand = f"../target/release/{binname}"

elif interpreter == "python":
    path = f"{historyfolder}/a.py"
    subprocess.call(f"cp ./src/a.py {path}", shell=True)
    bootcommand = f"pypy3 {path}"

if is_interactive:
    bootcommand = f"../target/release/tester {bootcommand}"


def run(path):
    name = path.replace(".txt", "")

    start = time.time()
    process = subprocess.Popen(
        "{} < {} 1> {} 2> {}".format(
            bootcommand,
            "tools/in/" + path,
            historyfolder + "/out/" + path,
            historyfolder + "/err/" + path
        ),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    while process.poll() is None:
        pass
    stop = time.time()

    with open(historyfolder + "/others/" + path, "w") as f:
        f.write("process_time = {}\n".format(stop - start))

    subprocess.call("cp ./tools/in/{path} {target}/in/{path}".format(
        target=historyfolder, path=path), shell=True)

    subprocess.call("mkdir -p __temp", shell=True)
    subprocess.call("mkdir -p __temp/{}".format(name), shell=True)
    subprocess.call("cd ./__temp/{}\n{} {} {} 1>> {err} 2>> {err}".format(
        name,
        os.path.abspath("../target/release/vis"),
        historyfolder + "/in/" + path,
        historyfolder + "/out/" + path,
        err=historyfolder + "/others/" + path), shell=True)

    if os.path.exists("./__temp/{}/vis.html".format(name)):
        subprocess.call("mv ./__temp/{}/vis.html {}".format(
            name,
            historyfolder + "/vis/" + name + ".svg"), shell=True)

        with open(historyfolder + "/vis/" + name + ".svg", "r") as f:
            svg = f.read()
        with open(historyfolder + "/vis/" + name + ".svg", "w") as f:
            svg = svg.replace("<html><body>", "")
            svg = svg.replace("</body></html>", "")
            f.write(svg)

    if os.path.exists("./__temp/{}/vis.png".format(name)):
        subprocess.call("mv ./__temp/{}/vis.png {}".format(
            name,
            historyfolder + "/vis/" + name + ".png"), shell=True)

    make_anime(f"{historyfolder}/err/{path}",
               f"{historyfolder}/anime/{name}.svg",
               f"{historyfolder}/others/{path}")

    print(path)


with multiprocessing.Pool(POOLCOUNT) as p:
    results = [p.apply_async(run, (path,))
               for path in sorted(os.listdir("./tools/in"))]
    for r in results:
        try:
            r.get()
        except Exception as e:
            print(e)
            exit()

oldfolder = historyfolder
import pathlib
historyfolder = pathlib.Path(historyfolder).parent / "pre"
if os.path.exists(historyfolder):
    subprocess.call("rm -rf {}".format(historyfolder), shell=True)
os.rename(oldfolder, historyfolder)

print("TestDone!!")

ahc_analyzer.main(historyfolder)
