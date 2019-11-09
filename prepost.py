import json
import os
import repo as Repo
import subprocess
import sys
import toml


def get_config_file_path():
    config_file_path = ''
    if os.getenv('XDG_CONFIG_HOME'):
        config_file_path = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'prepost', 'config.toml')
    else:
        config_file_path = os.path.join(os.getenv('HOME'), '.config', 'prepost', 'config.toml')

    if not os.path.exists(config_file_path):
        print('config file is not exists.')
        exit()

    return config_file_path


def main(mode):
    with open(get_config_file_path()) as f:
        config = toml.load(f)

    # print(json.dumps(config, indent=4, sort_keys=True, separators=(',', ': ')))
    # exit()

    item_list = []
    for repo in config.get(mode).get('repo'):
        item_list.append(Repo.repo(repo.get('path'), repo.get('data')))

    for item in item_list:
        print(item.get_path(), item.execute())


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 2:
        print('Usage: python prepost.py {pre|post}')
        exit()

    mode = argv[1]
    if mode != 'pre' and mode != 'post':
        print('Usage: python prepost.py {pre|post}')
        exit()

    main(mode)
