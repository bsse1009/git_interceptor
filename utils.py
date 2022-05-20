import os



CWD = os.getcwd()
PATH = f"{CWD}/.git/objects"

def find_files(filename, dir = PATH):
  result = []
  filename = filename[2:]
  for root, dir, files in os.walk(dir):  # Wlaking top-down from the root
    if filename in files:
      result.append(os.path.join(root, filename))
  return result



def convert_into_binary(file_path):
    with open(file_path, 'rb') as file:
        binary = file.read()

    return binary