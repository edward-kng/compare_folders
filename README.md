# Compare Folders

A Python script to compare two folders and find any missing files. The script ignores folder structure and will not count a file that has been moved or renamed in one folder as missing, as long as it exists in both folders.

Note: Symbolic links are ignored and hard links are treated as duplicate files.

## Usage
Download the script and run `python3 compare_folders.py </path/to/folder1> </path/to/folder2> [nr of threads]` in your terminal.

Threads are optional, but using multiple threads will likely improve performance.
