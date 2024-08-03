def delete_samples(targetfolder, case):
    import os
    import shutil
    import sys
    sys.path.append(os.path.abspath(os.path.join(targetfolder, "testcases")))
    module_path = os.path.join(targetfolder, "testcases", f"{case}.py")
    if os.path.exists(module_path.replace(".py", "/in")):
        shutil.rmtree(module_path.replace(".py", "/in"))
    if os.path.exists(module_path.replace(".py", "/out")):
        shutil.rmtree(module_path.replace(".py", "/out"))
    if os.path.exists(module_path.replace(".py", "")):
        os.mkdir(module_path.replace(".py", "/in"))
        os.mkdir(module_path.replace(".py", "/out"))

def make_samples(targetfolder, case, n):
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(targetfolder, "testcases")))
    module_path = os.path.join(targetfolder, "testcases", f"{case}.py")
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    module = __import__(module_name)
    for i in range(n):
        if hasattr(module, "main"):
            with open(module_path.replace(".py", f"/in/{i}.txt"), "w") as f:
                with open(module_path.replace(".py", f"/out/{i}.txt"), "w") as g:
                    sys.stdout = f
                    sys.stderr = g
                    try:
                        module.main()
                    except Exception as e:
                        sys.stdout = sys.__stdout__
                        sys.stderr = sys.__stderr__
                        import traceback
                        traceback.print_exc()
            
        else:
            print(f"module {module_name} has no main() function")

if __name__ == "__main__":
    delete_samples("./rust/_test", "a")
    make_samples("./rust/_test", "a", 1)
