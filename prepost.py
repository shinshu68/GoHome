from pathlib import Path
import json
import os
import subprocess
import sys
import toml


class Repo():
    def __init__(self, path, pre=None, post=None):
        self.path = path
        self._pre = pre
        self._post = post

    def __str__(self):
        return str({
            'path': self.path,
            'pre': self.pre,
            'post': self.post
        })

    def pre(self):
        os.chdir(Path(self.path).expanduser())
        print(os.getcwd())
        print(self.path, self._pre)

    def post(self):
        os.chdir(Path(self.path).expanduser())
        print(os.getcwd())
        print(self.path, self._post)


def get_config_file_path():
    config_file_path = ''
    if os.getenv('XDG_CONFIG_HOME'):
        config_file_path = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'prepost', 'config.toml')
    else:
        config_file_path = os.path.join(os.getenv('HOME'), '.config', 'prepost', 'config.toml')

    if not os.path.exists(config_file_path):
        print('config file is not exists.')

    return config_file_path


def main(mode='pre'):
    config_file = get_config_file_path()
    if config_file == "":
        exit()

    with open(config_file) as f:
        config = toml.load(f)

    # print(json.dumps(config, indent=4, sort_keys=True, separators=(',', ': ')))
    # exit()

    if 'repo' not in config:
        print('repo statement is not exists.')
        exit()

    repo_list = []
    for repo in config.get('repo'):
        repo_list.append(Repo(repo.get('path'), repo.get('pre'), repo.get('post')))

    for repo in repo_list:
        if mode == 'pre':
            repo.pre()
        else:
            repo.post()


if __name__ == '__main__':
    argv = sys.argv
    main()
