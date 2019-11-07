from pathlib import Path
import os
import git
import subprocess


class repo():
    pre_commands = ['pull']
    post_commands = ['push', 'commit']

    def __init__(self, path, data):
        self._path = path
        self._data = data
        if not self.is_valid_path():
            raise TypeError
        if not self.is_valid_data():
            raise TypeError

    def __str__(self):
        return str({
            'path': self.get_path(),
            'expand_path': self.get_expand_path(),
            'data': self.get_data()
        })

    def is_valid_path(self):
        if not os.path.exists(self.get_expand_path()) or not self.is_inside_work_tree():
            return False
        return True

    def is_valid_data(self):
        data = self.get_data()
        if 'local' not in data or len(data['local']) == 0:
            return False
        if 'check' not in data or len(data['check']) == 0:
            return False
        if 'remote' not in data or 'name' not in data['remote'] or'branch' not in data['remote']:
            return False
        return True

    def is_inside_work_tree(self):
        os.chdir(self.get_expand_path())
        res = subprocess.run('git rev-parse --is-inside-work-tree',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
        if res == 'true':
            return True
        else:
            return False

    def git_commit_distance(self, a, b):
        os.chdir(self.get_expand_path())
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

    def get_expand_path(self):
        return str(Path(self.get_path()).expanduser())

    def get_data(self):
        return self._data

    def execute(self):
        data = self.get_data()
        return True

    def is_pulled(self):
        os.chdir(self.get_expand_path())
        data = self.get_data()
        name = data['remote']['name']
        branch = data['remote']['branch']
        remote_branch = name + '/' + branch
        res = subprocess.run(f'git fetch --dry-run {name} {branch}',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
        if res != "":
            return False

        now_branch = subprocess.run('git symbolic-ref --short HEAD',
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
        res = subprocess.run(f'git checkout {data["local"]}',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if res.returncode != 0:
            return False

        res = self.git_commit_distance('HEAD', remote_branch)
        subprocess.run(f'git checkout {now_branch}',
                       shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        if 0 <= res:
            return True
        else:
            return False

    def is_pushed(self):
        os.chdir(self.get_expand_path())
        data = self.get_data()
        remote_branch = data['remote']['name'] + '/' + data['remote']['branch']
        res = self.git_commit_distance('HEAD', remote_branch)
        if res <= 0:
            return True
        else:
            return False
