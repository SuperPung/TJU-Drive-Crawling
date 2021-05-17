import time


def sec2time(million_seconds):
    time_stamp = round(million_seconds / 1000000)
    time_array = time.localtime(time_stamp)
    style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return style_time


class DirFile:
    docid: str
    modified: time
    name: str
    rev: str
    __size: str

    def __init__(self, docid, modified, name, rev, size):
        self.docid = docid
        self.modified = sec2time(modified)
        self.name = name
        self.rev = rev
        self.size = size

    def display(self):
        return '文件名：' + self.name + '，修改时间：' + self.modified + '，大小：' + self.size


class FileFile(DirFile):
    client_mtime: time

    def __init__(self, docid, modified, name, rev, size, client_mtime):
        super().__init__(docid, modified, name, rev, size)
        self.client_mtime = sec2time(client_mtime)

    def display(self):
        return '文件名：' + self.name + '，修改时间：' + self.client_mtime + '目录修改时间：' + self.modified + '，大小：' + self.size


class FileDict:
    root: dict

    def __init__(self, dirs: list, files: list):
        if isinstance(dirs, list) and isinstance(files, list):
            self.root = {'dirs': dirs, 'files': files}
        else:
            return


class FileList:
    root: list

    def __init__(self):
        self.root = []

    def add_file(self, file):
        if isinstance(file, DirFile) or isinstance(file, FileFile):
            self.root.append(file)
        else:
            return
