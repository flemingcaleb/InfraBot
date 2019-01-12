import glob   
import json


path = './lab_contents/*.json'   
files=glob.glob(path)   
for file in files:     
    f=open(file, 'r')  
    curObj = json.load(f)   
    print(curObj['name'])
    f.close()