import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
bin_name = sys.argv[1]
contest, name = bin_name.split('-')
path = os.path.join(os.path.curdir, contest, "src", name + '.py')
with open(path, 'r') as f:
    print(f.read())
