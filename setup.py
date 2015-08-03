import commands
import sys
import os
import re

path_list = sys.path

src_path = os.path.dirname(os.path.abspath(__file__)) + "/drfilter"
des_path = ""
for path in path_list:
    pattern = re.compile(r'.*python.*/.*packages$')
    match = pattern.match(str(path))
    if match:
        des_path = path

print src_path
print des_path
commands.getoutput('sudo ln -s ' + src_path + ' ' + des_path)
