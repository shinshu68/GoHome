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
        if not os.path.exists(self.get_expand_path()):
            raise TypeError(f'"{path}" is not exists.')
        if not self.is_inside_work_tree():
            raise TypeError(f'"{path}" is not inside git work tree.')

        # dataが有効かどうか
        # data['local']が有効かどうか
        if 'local' not in data:
            raise TypeError('"local" not in data')
        if not self.is_exists_local_branch():
            raise TypeError(f'"local" branch({data["local"]}) is not found in {path}.')

        # data['commands']が有効かどうか
        if 'commands' not in data:
            raise TypeError('"commands" not in data.')
        data['commands'] = set(data['commands'])
        if len(data['commands']) == 0:
            raise TypeError('"commands" is empty.')

        invalid_list = [command for command in data['commands'] if command not in self.valid_commands]
        if len(invalid_list) != 0:
            raise TypeError(f'"{invalid_list}" is not in valid_commands command.')

        # data['remote']が有効かどうか
        if 'remote' not in data:
            raise TypeError('"remote" not in data.')
        if 'name' not in data['remote']:
            raise TypeError('"name" not in data["remote"].')
        if 'branch' not in data['remote']:
            raise TypeError('"branch" not in data["remote"].')

        self._data = data

    def __str__(self):
        return str({
            'path': self.get_path(),
            'expand_path': self.get_expand_path(),
            'data': self.get_data()
        })

    def is_exists_local_branch(self):
        os.chdir(self.get_expand_path())
        local = self.get_data()['local']
        res = subprocess.run(f'git rev-parse --verify {local}',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        return True if res.returncode == 0 else False

    def is_inside_work_tree(self):
        os.chdir(self.get_expand_path())
        res = subprocess.run('git rev-parse --is-inside-work-tree',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).stdout.decode('utf-8').strip()

        return True if res == 'true' else False

    def is_exists_commit_hash(self, commit_hash):
        os.chdir(self.get_expand_path())
        res = subprocess.run(f'git rev-list {commit_hash}',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        return True if res.returncode == 0 else False

    # 2コミット間の距離を返す
    # ahead -> +, behind -> -, equal or ahead behind -> 0
    def git_commit_distance(self, a, b):
        os.chdir(self.get_expand_path())
        res = int(subprocess.run(f'git rev-list --count {a}...{b}',
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).stdout.decode('utf-8').strip())
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
            if command == 'push' and self.is_pushed():
                result['push'] = True

            elif command == 'pull' and self.is_pulled():
                result['pull'] = True

            elif command == 'commit' and self.is_committed():
                result['commit'] = True

            else:
                result[command] = False

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
        subprocess.run(f'git fetch --dry-run {name} {branch}',
                       shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
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

