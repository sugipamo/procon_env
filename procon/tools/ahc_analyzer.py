import os
import pandas as pd


GROUPS = []


def main(targetfolder):
    os.chdir(targetfolder)
    outputs = []
    paths = [p for p in os.listdir("./in") if p.endswith(".txt")]
    paths.sort()
    for path in paths:
        output = {}
        for name in ["err", "out", "others"]:
            with open("./" + name + "/" + path, "r") as f:
                for l in f.read().split("\n"):
                    if not " = " in l:
                        continue
                    x = l.split(" = ")[0]
                    y = l.split(" = ")[1].replace("\n", "")
                    try:
                        y = float(y)
                    except:
                        pass
                    output[x] = y

        import math

        if "score" in output:
            output["Score"] = output["score"]
        if "Score" in output:
            output["logscore"] = math.log(output["Score"] + 1)

        outputs.append(output)

    outputs = pd.DataFrame(outputs)
    outputs.index = paths

    pd.options.display.float_format = '{:.2f}'.format

    with open("./summary.txt", "w") as f:
        f.write("\n\n")
        f.write("all data\n")
        f.write(outputs.describe().to_string())
        f.write("\n\n\n")

        def group(name):
            outputss = outputs.groupby(name)
            for d, outputs_ in outputss:
                f.write(name + " = " + str(d) + "\n")
                f.write(outputs_.drop(columns=name).describe().to_string())
                f.write("\n\n\n")

        [group(g) for g in GROUPS]

        f.write(outputs.to_string())



    import shutil
    import pathlib
    path = pathlib.Path(targetfolder)
    import datetime
    path = path.parent
    if "Score" in outputs:
        mean_score = outputs["Score"].mean()
        print("MeanScore: ", mean_score)
        path = path / str(mean_score)
    else:
        path = path / datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    if path.exists():
        shutil.rmtree(path)
    shutil.copytree(targetfolder, path)

    # targetfolderの中から上位5つを残し、ほかを削除する
    folders = pathlib.Path(targetfolder).parent.glob("*")
    folders = sorted(folders, key=lambda x: x.name)
    # preフォルダを除く
    folders = [f for f in folders if not "pre" in f.name]
    folders = folders[:-5]
    [shutil.rmtree(f) for f in folders]
    
    print("Analyze Done!!")

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    targetfolder = sorted(os.listdir("./history"))[-1]
    targetfolder = "./history/" + targetfolder
    main(targetfolder)

