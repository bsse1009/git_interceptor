import os
import subprocess
import bson, pickle
import pymongo

PATH = "/home/ibrahim/Desktop/test/bitbucket/dbus-cpp/.git/objects"
os.chdir('/home/ibrahim/Desktop/test/bitbucket/dbus-cpp')
treeList = []
blobList = []

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["tasks_db_bitbucket"]
mycol = mydb["tasks"]

def find_files(filename, dir=PATH):
  result = []
  filename = filename[2:]
  for root, dir, files in os.walk(dir):  # Wlaking top-down from the root
    if filename in files:
        result.append(os.path.join(root, filename))
  return result


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
  commandTree = f'gitold cat-file -p {root} | grep tree'
  commandBlob = f'gitold cat-file -p {root} | grep blob'
  if not isValidObject(root, 'tree'):
    return
  trees = subprocess.getstatusoutput(commandTree)
  blobs = subprocess.getstatusoutput(commandBlob)
  blobs = blobs[1].split()[2::4]
  # print(trees[1])
  blobList += blobs
  if trees[1] == '' or 'fetal' in trees[1]:
    return
  treeObjects = trees[1].split()[2::4]
  # print(len(treeObjects))
  treeList += treeObjects
  for treeO in treeObjects:
    find_objects(treeO)


def convert_into_binary(file_path):
    with open(file_path, 'rb') as file:
        binary = file.read()

    return binary


commandRoot = 'gitold cat-file -p HEAD | grep tree'
Root = subprocess.getstatusoutput(commandRoot)
root = Root[1].split()[1]
rootDir = root[:2]
find_objects(root)

rootObject = (root, convert_into_binary(find_files(root)[0]))
treeObjects = [(tree, convert_into_binary(find_files(tree)[0])) for tree in treeList]
blobObjects = [(blob, convert_into_binary(find_files(blob)[0])) for blob in blobList]

object_dict = {}

object_dict['objects'] = {
        'commit': bson.Binary(pickle.dumps(rootObject)),
        'trees': bson.Binary(pickle.dumps(treeObjects)),
        'blobs': bson.Binary(pickle.dumps(blobObjects))
    }

x = mycol.insert_one(object_dict)
print(f"inserted successfully {x.inserted_id}")
myclient.close()

