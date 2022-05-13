from operator import le
import pymongo
import pickle
import os
import subprocess


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["tasks_db_test1"]
mycol = mydb["tasks"]

record = mycol.find_one({})
objects = record['objects']
# print(objects)
commit = pickle.loads(objects["commit"])
trees = pickle.loads(objects["trees"])
blobs = pickle.loads(objects["blobs"])

objects = [commit]+trees+blobs

PATH = "/home/ibrahim/Desktop/test/test1Res"

os.chdir(PATH)
os.system('gitold init')
os.chdir('.git/objects/')

for obj in objects:
    name, content = obj
    dir, file = name[:2], name[2:]
    try:
        os.mkdir(dir)
    except Exception as ex:
        assert True
    with open(f"{dir}/{file}", 'wb') as f:
        f.write(content)


os.chdir(PATH)
command = "gitold cat-file -p"

def isValidObject(treeHash, type):
    if len(treeHash) != 40:
        return False
    try:
        if subprocess.getstatusoutput(f"gitold cat-file -t {treeHash}")[1] != type:
            # print(subprocess.getstatusoutput(f"gitold cat-file -t {treeHash}")[1])
            return False
    except Exception as e:
        return False
    return True

def writeFile(fileName, contetnt):
    with open(fileName, 'w', encoding= 'unicode_escape') as f:
        f.write(contetnt)

def writeBinaryFiles(fileName, content):
    pass

def treeTraverse(treeHash, dirName=None):
    try:
        os.mkdir(dirName)
    except Exception as ex:
        assert True
    if not isValidObject(treeHash, 'tree'):
        return
    files = subprocess.getstatusoutput(f"{command} {treeHash} | grep blob")[1].split()
    dirs = subprocess.getstatusoutput(f"{command} {treeHash} | grep tree")[1].split()
    fileObjects = files[2::4]
    fileNames = files[3::4]
    
    for i in range (0, len(fileObjects)):
        if dirName == None:
            fileName = fileNames[i]
        else:
            fileName = f"{dirName}/{fileNames[i]}"
        if not isValidObject(fileObjects[i], 'blob'):
            continue
        try:
            fileContent = subprocess.getstatusoutput(f"{command} {fileObjects[i]}")[1]
            writeFile(fileName, fileContent)
        except Exception as ex:
            writeBinaryFiles(fileName, fileObjects[i])
            assert True
    
    treeObjecs = dirs[2::4]
    dirNames = dirs[3::4]

    for i in range (0, len(treeObjecs)):
        if dirName == None:
            dirName = dirNames[i]
        else:
            dirName = f"{dirName}/{dirNames[i]}"
        tree = treeObjecs[i]
        if not isValidObject(tree, 'tree'):
            continue
        treeTraverse(tree, dirName)
        dirNameSplit = dirName.split('/')[:-1]
        dirName = '/'.join(dirNameSplit) 

treeTraverse(commit[0])