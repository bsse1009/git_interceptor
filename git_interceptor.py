import os
import sys
from git import Repo
import time
import json
import pymongo
import bson
import pickle

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["tasks_db"]
mycol = mydb["tasks"]
cwd = os.getcwd()
firstCommand = os.path.basename(sys.argv[0])

# argv = input("Enter command:$  ").strip().split()
is_commit = firstCommand == 'git' and sys.argv[1] == 'commit'
tasks_dict = {}
with open('tasks.json', 'r') as f:
    tasks_dict = json.load(f)

# projectId = input("enter current project: ")
# boardId = input("enter current board: ")

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

current_task = get_current_task()
print(current_task)
uid = 11

object_dict = {
    'user_id': uid,
    'task_id': current_task["id"]
}
print(f'{cwd}/.git')
if is_commit:
    # print(f"User commited a task")
    repo = Repo(f'{cwd}/.git')
    latest_commit = repo.head.commit
    root = latest_commit.tree
    # print(root)
    author = latest_commit.author.name
    commited_time = time.strftime("%a, %d %b %Y %H:%M", time.gmtime(latest_commit.committed_date))
    trees = root.trees
    blobs = [tree.blobs for tree in trees]
    object_dict['objects'] = {
        'commit': bson.Binary(pickle.dumps(root)),
        'trees': bson.Binary(pickle.dumps(trees)),
        'blobs': bson.Binary(pickle.dumps(blobs+root.blobs))
    }
    x = mycol.insert_one(object_dict)
    print(f"inserted successfully {x.inserted_id}")
    myclient.close()

try:
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
    assert True
command = ' '.join(sys.argv)
file = open('log.txt','a+')
file.write(command)
file.write('\n')
file.close()
os.system(command)

