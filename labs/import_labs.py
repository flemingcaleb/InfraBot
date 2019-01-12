import glob   
import json

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
import Database

path = './lab_contents/*.json'   
files=glob.glob(path)   
for file in files:     
    f=open(file, 'r')  
    curObj = json.load(f)   
    newLab = Database.Labs()
    newLab.name = curObj['name']
    newLab.workspace_id = curObj['workspace_id']
    newLab.url = curObj['url']
    newLab.difficulty = curObj['url']
    newLab.possible_score = curObj['max_score']
    print(newLab.id)
    f.close()