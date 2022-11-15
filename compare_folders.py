from hashlib import sha256
from threading import Thread, Lock, active_count
import sys
import os

class Reader:
    def __init__(self, dir1, dir2):
        self._dirs = (dir1, dir2)
        self._lock = Lock()
        self._nr_bytes = 0
        self._nr_bytes_read = 0
        self._data = ({}, {})
        self._threads = []

    def _count_bytes(self, path):
        for item in os.listdir(path):
            item_path = path + "/" + item

            if os.path.isdir(item_path):
                self._make_thread(self._count_bytes, (item_path,))
            elif not os.path.islink(item_path):
                self._lock.acquire()

                self._nr_bytes += os.path.getsize(item_path)

                self._lock.release()

    def _read_files(self, path, dict):
        for item in os.listdir(path):
            item_path = path + "/" + item

            if os.path.isdir(item_path):
                self._make_thread(self._read_files, (item_path, dict))
            elif not os.path.islink(item_path):
                self._make_thread(self._read_file, (item_path, dict))
                

    def _read_file(self, path, dict):
        file = open(path, "rb")
        data = file.read()
        file.close()
        checksum = sha256(data).hexdigest()

        self._lock.acquire()

        self._nr_bytes_read += os.path.getsize(path)

        if self._nr_bytes > 0:
            sys.stdout.write(
                "\rReading files... "
                + "{:.2f}".format(
                    round((self._nr_bytes_read / self._nr_bytes) * 100, 2)
                ) + "%"
            )

        if not checksum in dict:
            dict[checksum] = []
        
        dict[checksum].append(path)

        self._lock.release()

    def _make_thread(self, functionName, functionArgs):
        if active_count() < NR_THREADS:
            self._lock.acquire()

            thread = Thread(
                    target=functionName,
                    args=functionArgs
                )
            
            thread.start()
            self._threads.append(thread)

            self._lock.release()
        else:
            functionName(*functionArgs)

    def read(self):
        for i in range(2):
            self._make_thread(self._count_bytes, (self._dirs[i],))

        sys.stdout.write("\nCounting folder sizes...")

        for thread in self._threads:
            thread.join()

        self._threads = []

        for i in range(2):
            self._make_thread(self._read_files, (self._dirs[i], self._data[i]))

        for thread in self._threads:
            thread.join()

        return self._data

def get_diffs(dir1_path, dir2_path, checksums_dir1, checksums_dir2):
    diffs_found = False

    for file in checksums_dir1:
            if not file in checksums_dir2:
                if not diffs_found:
                    print(f"\n\nFiles found in {dir1_path} that were missing or changed in {dir2_path}:")
                    diffs_found = True
                
                print("\n\tFile located at: ")

                for path in checksums_dir1[file]:
                    print("\t\t" + path)

def main():
    if len(sys.argv) < 3:
        print("Error: Too few arguments")
        exit(1)

    global NR_THREADS

    if len(sys.argv) > 3:
        try:
            NR_THREADS = int(sys.argv[3])
        except:
            print("Error: Number of threads must be an integer")
            exit(2)
    else:
        NR_THREADS = 1

    dirs = (sys.argv[1], sys.argv[2])
    reader = Reader(dirs[0], dirs[1])
    data = reader.read()
    
    if data[0].keys() == data[1].keys():
        print(f"\n\nNo differences found. {dirs[0]} and {dirs[1]} contain all the same files.")
    else:
        get_diffs(dirs[0], dirs[1], data[0], data[1])
        get_diffs(dirs[1], dirs[0], data[1], data[0])

if __name__ == "__main__":
    main()
