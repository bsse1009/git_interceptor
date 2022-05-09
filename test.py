import pymongo
import pickle
import os
import subprocess


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydb"]
mycol = mydb["tasks"]

record = mycol.find_one({})
objects = record['objects']
# print(objects)
commit = pickle.loads(objects["commit"])
trees = pickle.loads(objects["trees"])
blobs = pickle.loads(objects["blobs"])

objects = [commit]+trees+blobs

PATH = "/home/ibrahim/Desktop/AllTest/test2"

os.chdir(PATH)
os.system('gitold init')
os.chdir('.git/objects/')

for obj in objects:
    name, content = obj
    dir, file = name[:2], name[2:]
    os.mkdir(dir)
    with open(f"{dir}/{file}", 'wb') as f:
        f.write(content)


os.chdir(PATH)
command = "gitold cat-file -p"

def writeFile(fileName, contetnt):
    with open(fileName, 'w') as f:
        f.write(contetnt)

def treeTraverse(treeHash, dirName=None):
    if dirName != None:
        os.mkdir(dirName)
    files = subprocess.getstatusoutput(f"{command} {treeHash} | grep blob")[1].split()
    dirs = subprocess.getstatusoutput(f"{command} {treeHash} | grep tree")[1].split()
    fileObjects = files[2::4]
    fileNames = files[3::4]
    
    for i in range (0, len(fileObjects)):
        if dirName == None:
            fileName = fileNames[i]
        else:
            fileName = f"{dirName}/{fileNames[i]}"
        fileContent = subprocess.getstatusoutput(f"{command} {fileObjects[i]}")[1]
        print(fileContent)
        writeFile(fileName, fileContent)
    
    treeObjecs = dirs[2::4]
    dirNames = dirs[3::4]

    for i in range (0, len(treeObjecs)):
        if dirName == None:
            dirName = dirNames[i]
        else:
            dirName = f"{dirName}/{dirNames[i]}"
        tree = treeObjecs[i]
        treeTraverse(tree, dirName)


print(commit[0])
treeTraverse(commit[0])