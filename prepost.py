import json
import os
import repo as Repo
import subprocess
import sys
import toml
from multiprocessing import Process
from multiprocessing import Pipe


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


def repo_create_execute(repo, send_rev):
    item = Repo.repo(repo.get('path'), repo.get('data'))
    send_rev.send((item.get_path(), item.execute()))


def main(mode):
    with open(get_config_file_path()) as f:
        config = toml.load(f)

    # print(json.dumps(config, indent=4, sort_keys=True, separators=(',', ': ')))
    # exit()

    pipe_list = []
    process_list = []
    for repo in config.get(mode).get('repo'):
        get_rev, send_rev = Pipe(False)
        process = Process(target=repo_create_execute, args=(repo, send_rev))
        process_list.append(process)
        pipe_list.append(get_rev)
        process.start()

    for process in process_list:
        process.join()

    result_list = [x.recv() for x in pipe_list]
    for res in result_list:
        print(res)


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
