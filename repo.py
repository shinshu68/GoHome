from pathlib import Path
import os


class repo():
    def __init__(self, path, pre=None, post=None):
        self.path = path
        self._pre = pre
        self._post = post

    def __str__(self):
        return str({
            'path': self.path,
            'pre': self._pre,
            'post': self._post
        })

    def get_pre(self):
        return self._pre

    def get_post(self):
        return self._post

    def pre(self):
        os.chdir(Path(self.path).expanduser())
        print(os.getcwd())
        print(self.path, self._pre)

    def post(self):
        os.chdir(Path(self.path).expanduser())
        print(os.getcwd())
        print(self.path, self._post)
