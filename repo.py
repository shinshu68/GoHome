from pathlib import Path
import os
import git
import subprocess


class repo():
    def __init__(self, path, pre=None, post=None):
        _path = str(Path(path).expanduser())
        self.is_valid_path(_path)
        self.path = _path
        self._pre = pre
        self._post = post

    def __str__(self):
        return str({
            'path': self.path,
            'pre': self.get_pre(),
            'post': self.get_post()
        })

    def is_valid_path(self, path):
        if not os.path.exists(path) or not self.is_inside_work_tree(path):
            raise ValueError
        return True

    def is_inside_work_tree(self, path):
        os.chdir(path)
        res = subprocess.run(f'git rev-parse --is-inside-work-tree',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
        if res == 'true':
            return True
        else:
            return False

    def get_pre(self):
        return self._pre

    def get_post(self):
        return self._post

    def pre(self):
        pre = self.get_pre()
        if 'check' not in pre or len(pre['check']) == 0:
            raise ValueError
        if 'remote' not in pre:
            raise ValueError

        os.chdir(self.path)
        repo = git.Repo(self.path, search_parent_directories=True)
        # for check in pre['check']:


    def post(self):
        post = self.get_post()
        if 'check' not in post or len(post['check']) == 0:
            raise ValueError
        if 'remote' not in post:
            raise ValueError
