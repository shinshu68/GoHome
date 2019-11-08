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
            raise TypeError('path is not exists or path is not inside git work tree.')

        # dataが有効かどうか
        if 'local' not in data or len(data['local']) == 0:
            raise TypeError('local not in data or local length is 0.')
        if 'commands' not in data or len(data['commands']) == 0:
            raise TypeError('commands not in data or commands length is 0.')
        if not all(map(lambda x: x in self.valid_commands, data['commands'])):
            raise TypeError('found not in valid_commands command.')
        if 'remote' not in data or 'name' not in data['remote'] or 'branch' not in data['remote']:
            raise TypeError('remote not in data or (name or branch) not in remote.')

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

        return True if res == 'true' else False

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
        result = {}
        for command in data['commands']:
            if command == 'push' and not self.is_pushed():
                result['push'] = False

            elif command == 'pull' and not self.is_pulled():
                result['pull'] = False

            elif command == 'commit' and not self.is_committed():
                result['commit'] = False

            else:
                result[command] = True

        return result

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

    @checkout_undo
    def is_pulled(self):
        data = self.get_data()
        name = data['remote']['name']
        branch = data['remote']['branch']
        remote_head = subprocess.run(f'git ls-remote {name} {branch}',
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE).stdout.decode('utf-8').strip().split()[0]

        val = self.git_commit_distance('HEAD', remote_head)

        return True if val <= 0 else False

    @checkout_undo
    def is_pushed(self):
        data = self.get_data()
        remote_branch = data['remote']['name'] + '/' + data['remote']['branch']

        val = self.git_commit_distance('HEAD', remote_branch)

        return True if 0 <= val else False

    @checkout_undo
    def is_committed(self):
        res = subprocess.run('git diff -name-only',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).stdout.decode('utf-8').strip().split()

        return True if len(res) == 0 else False

