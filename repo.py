from pathlib import Path
import os
import git
import subprocess


class repo():
    valid_commands = ['push', 'commit', 'pull']

    def __init__(self, path, data):
        self._path = path
        self._data = data

        # pathが有効かどうか
        if not os.path.exists(self.get_expand_path()) or not self.is_inside_work_tree():
            raise TypeError

        # dataが有効かどうか
        if 'local' not in data or len(data['local']) == 0:
            raise TypeError
        if 'commands' not in data or len(data['commands']) == 0:
            raise TypeError
        if 'remote' not in data or 'name' not in data['remote'] or'branch' not in data['remote']:
            raise TypeError

    def __str__(self):
        return str({
            'path': self.get_path(),
            'expand_path': self.get_expand_path(),
            'data': self.get_data()
        })

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

    # 2コミット間の距離を返す
    # ahead -> +, behind -> -, equal or ahead behind -> 0
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

    # dataに保存されているlocalブランチにcheckoutした後、
    # 関数を実行し、元々のブランチに戻る
    def checkout_undo(func):
        def wrapper(self, *args, **kwargs):
            os.chdir(self.get_expand_path())
            data = self.get_data()
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

            val = func(self, *args, **kwargs)

            subprocess.run(f'git checkout {now_branch}',
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            return val
        return wrapper

    # remoteをfetchする
    def git_fetch(func):
        def wrapper(self, *args, **kwargs):
            os.chdir(self.get_expand_path())
            data = self.get_data()
            name = data['remote']['name']
            branch = data['remote']['branch']
            res = subprocess.run(f'git fetch --dry-run {name} {branch}',
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
            if res != "":
                return False
            val = func(self, *args, **kwargs)
            return val
        return wrapper

    @git_fetch
    @checkout_undo
    def is_pulled(self):
        data = self.get_data()
        remote_branch = data['remote']['name'] + '/' + data['remote']['branch']
        val = self.git_commit_distance('HEAD', remote_branch)
        if 0 <= val:
            return True
        else:
            return False

    @checkout_undo
    def is_pushed(self):
        data = self.get_data()
        remote_branch = data['remote']['name'] + '/' + data['remote']['branch']
        val = self.git_commit_distance('HEAD', remote_branch)
        if val <= 0:
            return True
        else:
            return False


