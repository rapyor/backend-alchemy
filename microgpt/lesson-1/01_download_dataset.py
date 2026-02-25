
import os
import urllib.request

NAMES_URL = "https://raw.githubusercontent.com/karpathy/makemore/refs/heads/master/names.txt"
DATA_PATH = "input.txt"

# we ensure a path file exist and if not, we download
def ensure_file_exist(path: str = DATA_PATH) -> str:
    if os.path.exists(NAMES_URL):
        print("The file path already exists.")
    else:
        print(f"[downloading...] - {path} ")
        urllib.request.urlretrieve(NAMES_URL, path)
        print(f"[downloaded] save to {path}")
    return path

if __name__ == "__main__":
    ensure_file_exist()