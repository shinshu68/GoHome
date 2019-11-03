from pathlib import Path
import os


class repo():
    def __init__(self, path, pre=None, post=None):
        self.path = str(Path(path).expanduser())
        self._pre = pre
        self._post = post

    def __str__(self):
        return str({
            'path': self.path,
            'pre': self.get_pre(),
            'post': self.get_post()
        })

    def get_pre(self):
        return self._pre

    def get_post(self):
        return self._post

    def pre(self):
        if not os.path.exists(self.path):
            # print(self.path)
            pass
        # os.chdir(Path(self.path).expanduser())
        # print(os.getcwd())

        pre = self.get_pre()
        if 'branch' not in pre:
            raise ValueError
        if 'check' not in pre or len(pre['check']) == 0:
            raise ValueError

    def post(self):
        if not os.path.exists(self.path):
            # print(self.path)
            pass
        # os.chdir(Path(self.path).expanduser())
        # print(os.getcwd())

        post = self.get_post()
        if 'branch' not in post:
            raise ValueError
        if 'check' not in post or len(post['check']) == 0:
            raise ValueError
