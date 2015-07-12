import commands
import sys
import os

path_list = sys.path

src_path = os.path.dirname(os.path.abspath(__file__)) + "/drfilter"
des_path = ""
for path in path_list:
    if str(path).endswith('python2.7/dist-packages'):
        des_path = path

print src_path
print des_path
commands.getoutput('sudo ln -s ' + src_path + ' ' + des_path)
