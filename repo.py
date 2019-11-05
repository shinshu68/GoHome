from pathlib import Path
import os
import git
import subprocess


class repo():
    pre_commands = ['pull']
    post_commands = ['push', 'commit']

    def __init__(self, path, pre=None, post=None):
        self._path = str(Path(path).expanduser())
        self._pre = pre
        self._post = post

    def __str__(self):
        return str({
            'path': self.get_path(),
            'pre': self.get_pre(),
            'post': self.get_post()
        })

    def is_valid_path(self, path):
        if not os.path.exists(path) or not self.is_inside_work_tree(path):
            return False
        return True

    def is_valid_data(self, data):
        if 'check' not in data or len(data['check']) == 0:
            return False
        if 'remote' not in data:
            return False
        if 'name' not in data['remote'] or'branch' not in data['remote']:
            return False
        return True

    def is_inside_work_tree(self, path):
        os.chdir(path)
        res = subprocess.run('git rev-parse --is-inside-work-tree',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
        if res == 'true':
            return True
        else:
            return False

    def git_commit_distance(self, a, b):
        os.chdir(self.get_path())
        res = subprocess.run(f'git rev-list --count {a}...{b}',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
        res = int(res)
        if res == 0:
            return 0

        lr = subprocess.run(f'git rev-list --left-right {a}...{b}',
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE).stdout.decode('utf-8').strip().split()
        if all(map(lambda x: x[0] == '>', lr)):
            return res
        if all(map(lambda x: x[0] == '<', lr)):
            return -1 * res

        return 0

    def get_path(self):
        return self._path

    def get_pre(self):
        return self._pre

    def get_post(self):
        return self._post

    def pre(self):
        pre = self.get_pre()
        if not self.is_valid_path(self.get_path()):
            return False
        if not self.is_valid_data(pre):
            return False
        # for check in pre['check']:
        #     if check in self.pre_commands:
        #         print(check)
        return True

    def post(self):
        post = self.get_post()
        if not self.is_valid_path(self.get_path()):
            return False
        if not self.is_valid_data(post):
            return False

        return True

    def is_pulled(self, data):
        os.chdir(self.get_path())
        name = data['remote']['name']
        branch = data['remote']['branch']
        remote_branch = name + '/' + branch
        subprocess.run(f'git fetch {name} {branch}',
                       shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        res = subprocess.run(f'git diff {remote_branch}',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if res.returncode != 0:
            return False

        res = res.stdout.decode('utf-8').strip()
        if res == '':
            return False
        else:
            return True

    def is_pushed(self, data):
        os.chdir(self.get_path())
        remote_branch = data['remote']['name'] + '/' + data['remote']['branch']
        res = subprocess.run(f'git diff {remote_branch}',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if res.returncode != 0:
            return False

        res = res.stdout.decode('utf-8').strip()
        if res == '':
            return True
        else:
            return False
