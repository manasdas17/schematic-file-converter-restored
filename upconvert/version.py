import os
import subprocess

def version():
    try:
        if os.path.exists(".git/hooks/post-commit.version"):
            subprocess.call([".git/hooks/post-commit.version"])
        with open('version', 'r') as f:
            version = f.read().strip()
    except:
        version = '0.6'
    
    return version
