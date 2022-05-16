import os
import sys
import json
import pymongo
import bson
import pickle
import subprocess
from utils import *

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydb"]
mycol = mydb["tasks"]
cwd = os.getcwd()
PATH = f"{cwd}/.git/objects"
treeList = []
blobList = []

is_commit = sys.argv[0] == 'git' and sys.argv[1] == 'commit'
tasks_dict = {}
with open('/home/ibrahim/Desktop/git/git_interceptor/tasks.json', 'r') as f:
    tasks_dict = json.load(f)


projectId = "1"
boardId = "12"
currentProject = [project for project in tasks_dict["project"] if project["id"] == projectId][0]
currentBoard = [board for board in currentProject["board"] if board["id"] == boardId][0]


def get_current_task():
    tasks = currentBoard["tasks"]
    last_end = '00: 00: 00'
    latest_task = None
    for task in tasks:
        last_end_task = sorted(task["times"], key=lambda d: d['end'])[-1]['end']
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

def find_objects(root):
  global treeList
  global blobList
  if not isValidObject(root, 'tree'):
    return
  commandTree = f'gitold cat-file -p {root} | grep tree'
  commandBlob = f'gitold cat-file -p {root} | grep blob'
  trees = subprocess.getstatusoutput(commandTree)
  blobs = subprocess.getstatusoutput(commandBlob)
  blobs = blobs[1].split()[2::4]
  blobList += blobs
  if trees[1] == '' or 'fetal' in trees[1]:
    return
  treeObjects = trees[1].split()[2::4]
  treeList += treeObjects
  for treeO in treeObjects:
    find_objects(treeO)

current_task = get_current_task()
# print(current_task)
uid = 11

object_dict = {
    'user_id': uid,
    'task_id': current_task["id"]
}

if is_commit:
    commandRoot = 'gitold cat-file -p HEAD | grep tree'
    Root = subprocess.getstatusoutput(commandRoot)
    root = Root[1].split()[1]
    rootDir = root[:2]
    find_objects(root)

    rootObject = (root, convert_into_binary(find_files(root, PATH)[0]))
    treeObjects = [(tree, convert_into_binary(find_files(tree, PATH)[0])) for tree in treeList]
    blobObjects = [(blob, convert_into_binary(find_files(blob, PATH)[0])) for blob in blobList]

    object_dict['objects'] = {
        'commit': bson.Binary(pickle.dumps(rootObject)),
        'trees': bson.Binary(pickle.dumps(treeObjects)),
        'blobs': bson.Binary(pickle.dumps(blobObjects))
    }
    
    x = mycol.insert_one(object_dict)
    print(f"inserted successfully {x.inserted_id}")
    myclient.close()

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
file = open('log.txt','a+')
file.write(command)
file.write('\n')
file.close()
os.system(command)