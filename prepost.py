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


def main(mode='pre'):
    config_file = get_config_file_path()

    with open(config_file) as f:
        config = toml.load(f)

    # print(json.dumps(config, indent=4, sort_keys=True, separators=(',', ': ')))
    # exit()

    pre_list = []
    for repo in config.get('pre').get('repo'):
        pre_list.append(Repo.repo(repo.get('path'), repo.get('data')))

    post_list = []
    for repo in config.get('post').get('repo'):
        post_list.append(Repo.repo(repo.get('path'), repo.get('data')))

    for pre in pre_list:
        print(pre.execute())

    for post in post_list:
        print(post.execute())


if __name__ == '__main__':
    argv = sys.argv
    main()
