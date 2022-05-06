# Git Interceptor
Git interceptor is a python program that intercept system git command and forward it to git.

## Environment setup
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```
## Create .exe file
For executable file we run the following command:
```
pyinstaller --noconfirm --onedir --console --onefile git_interceptor.py
```
It will create a git_interceptor.exe file in your_repo/dist directory. Rename the exe file with git.
## System set-up for Linux
Run following two command.
```
sudo cp /bin/git /bin/gitold
sudo cp your_dir/dist/git /bin/
```

