from os import listdir
from secrets import randbelow
from shutil import copy2
from pathlib import Path

src_dir = Path("TODO_perfect-human-expert-15-played")
dest_dir = Path("EVAL-perfect-human-expert-15-played")


chosen_files = []
file_list = listdir(src_dir)[1:]

for i in range(256):
    chosen_files.append(file_list.pop(randbelow(len(file_list))))

for file in chosen_files:
    copy2(src_dir / file, dest_dir / file)