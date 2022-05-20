import os
import sys
import json
import pymongo
import bson
import pickle
import subprocess
from sys import platform

from utils import *

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
myDB = mongoClient["mydb"]
myCollection = myDB["tasks"]
CWD = os.getcwd()
PATH = f"{CWD}/.git/objects"
jsonPath = 'C:/Users/user/Desktop/git_interceptor/tasks.json'

uID = 11
projectID = "1"
boardID = "12"
treeList = []
blobList = []
taskDict = {}
objectDict = {}
system = "linux"
filter = "grep"

try:
    if platform == "linux" or platform == "linux2":
        system = "linux"
    elif platform == "darwin":
        system = "OS X"
    elif platform == "win32":
        system = "windows"

    filter = "grep" if system == "linux" else "findstr"
    isCommit = sys.argv[0] == 'git' and sys.argv[1] == 'commit'
    with open(jsonPath, 'r') as f:
        taskDict = json.load(f)
    currentProject = [project for project in taskDict["project"]
                      if project["id"] == projectID][0]
    currentBoard = [board for board in currentProject["board"]
                    if board["id"] == boardID][0]
except Exception as e:
    assert True


def getCurrentTask():
    tasks = currentBoard["tasks"]
    last_end = '00: 00: 00'
    latest_task = None
    for task in tasks:
        last_end_task = sorted(
            task["times"], key=lambda d: d['end'])[-1]['end']
        if last_end < last_end_task:
            last_end = last_end_task
            latest_task = task
    return latest_task


def isValidObject(treeHash, type):
    if len(treeHash) != 40:
        return False
    try:
        if subprocess.getstatusoutput(f"gitold cat-file -t {treeHash}")[1] != type:
            return False
    except Exception as e:
        return False
    return True


def findObjects(root):
    global treeList
    global blobList
    if not isValidObject(root, 'tree'):
        return
    commandTree = f'gitold cat-file -p {root} | {filter} tree'
    commandBlob = f'gitold cat-file -p {root} | {filter} blob'
    trees = subprocess.getstatusoutput(commandTree)
    blobs = subprocess.getstatusoutput(commandBlob)
    blobs = blobs[1].split()[2::4]
    blobList += blobs
    if trees[1] == '' or 'fetal' in trees[1]:
        return
    treeObjects = trees[1].split()[2::4]
    treeList += treeObjects
    for treeO in treeObjects:
        findObjects(treeO)


currentTask = getCurrentTask()
objectDict['uID'] = uID
objectDict['taskID'] = currentTask['id']

if isCommit:
    commandRoot = f'gitold cat-file -p HEAD | {filter} tree'
    Root = subprocess.getstatusoutput(commandRoot)
    root = Root[1].split()[1]
    rootDir = root[:2]
    findObjects(root)

    rootObject = (root, convert_into_binary(find_files(root, PATH)[0]))
    treeObjects = [(tree, convert_into_binary(find_files(tree)[0])) if
                   isValidObject(tree, 'tree') else None
                   for tree in treeList]
    blobObjects = [(blob, convert_into_binary(find_files(blob)[0])) if
                   isValidObject(blob, 'blob') else None
                   for blob in blobList]

    treeObjects = [value for value in treeObjects if value != None]
    blobObjects = [value for value in blobObjects if value != None]

    objectDict['objects'] = {
        'commit': bson.Binary(pickle.dumps(rootObject)),
        'trees': bson.Binary(pickle.dumps(treeObjects)),
        'blobs': bson.Binary(pickle.dumps(blobObjects))
    }

    x = myCollection.insert_one(objectDict)
    print(f"inserted successfully {x.inserted_id}")
    mongoClient.close()

try:
    firstCommand = os.path.basename(sys.argv[0])
    firstCommandSplits = firstCommand.split(".")
    if "." not in firstCommand:
        firstCommand = firstCommand.replace(firstCommand,
                                            f'{sys.argv[0]}old')
    else:
        firstCommandWord = firstCommandSplits[0]
        firstCommandExtension = firstCommandSplits[1]
        firstCommand = firstCommand.replace(sys.argv[0],
                                            f'{firstCommandWord}old.{firstCommandExtension}')
    sys.argv[0] = firstCommand
except Exception as ex:
    assert True, ex
command = ' '.join(sys.argv)
file = open('log.txt', 'a+')
file.write(command)
file.write('/n')
file.close()
os.system(command)
