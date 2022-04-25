import os
import sys

try:
    print(''.join(sys.argv))
    firstCommand = os.path.basename(sys.argv[0])
    print(f'raw: {firstCommand}')
    firstCommandSplits = firstCommand.split(".")
    print(f'after split: {firstCommandSplits}')
    if "." not in firstCommand:
        firstCommand = firstCommand.replace(firstCommand,
        f'{sys.argv[0]}old')
        print(f'without dot final: {firstCommand}')
    else:
        firstCommandWord = firstCommandSplits[0]
        print(f'first command string: {firstCommandWord}')
        firstCommandExtension = firstCommandSplits[1]
        print(f'first command extension: {firstCommandWord}')
        firstCommand = firstCommand.replace(sys.argv[0], 
        f'{firstCommandWord}old.{firstCommandExtension}')
        print(f'with dot final {firstCommand}')
    sys.argv[0] = firstCommand
except Exception as ex:
    assert True
command = ' '.join(sys.argv)
print(f'saved log: {command}')
file = open('log.txt','a+')
file.write(command)
file.write('\n')
file.close()
os.system(command)
# pyinstaller --noconfirm --onedir --console  "C:/projects/automated_timeentry/git/git.py"
