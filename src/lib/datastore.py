import json, os, shutil

class DataStore(dict):
    """
    A persistent dictonary store that loads and saves data to disk.
    """

    def __init__(self, filename, data={}, flag='c', mode=None, **kwds):
        self.flag = flag        # r for readonly, c for create, n for new
        self.mode = mode        # None or octal triple for file permissions, e.g. 0644
        self.filename = filename    # path to the file on disk
        dict.__init__(self, data, **kwds)


        if flag != "n" and os.access(filename, os.R_OK):
            with open(filename, 'r') as fileobj:
                self.load(fileobj)



    def sync(self):
        # Write the dict to disk
        if self.flag == "r": return
        filename = self.filename
        tempname = filename + ".tmp"

        try:
            with open(tempname, 'w') as fileobj:
                self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise

        shutil.move(tempname, self.filename)

        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        json.dump(self, fileobj, separators=(',', ':'))

    def load(self, fileobj):
        fileobj.seek(0)

        try:
            self.update(json.load(fileobj))
        except Exception:
            raise ValueError("File is not valid JSON")
