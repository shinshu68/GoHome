from multiprocessing import Pipe
from multiprocessing import Process
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


def left_fill_asterisk(func):
    def wrapper(*args, **kwargs):
        s = ''
        if len(args) != 0:
            s = func(args[0], **kwargs)
        else:
            s = func(*args, **kwargs)
        column, _ = os.get_terminal_size()
        asterisks = '*' * (column - len(s) - 1)
        return s + ' ' + asterisks
    return wrapper


@left_fill_asterisk
def view_play_line(config_file_path):
    s = f'PLAY [config : {config_file_path}]'
    return s


@left_fill_asterisk
def view_task_line(task):
    s = f'TASK [{task["kind"]} : {task["path"]}]'
    return s


@left_fill_asterisk
def view_recap_line():
    s = 'PLAY RECAP'
    return s


def set_green(s):
    green = '\x1b[0;32m'
    return green + s


def set_red(s):
    red = '\x1b[0;31m'
    return red + s


def color_reset(s):
    reset = '\x1b[0;39m'
    return s + reset


def view_repo_line(data, command, status):
    local = data['local']
    remote = {
        data['remote']['name'],
        data['remote']['branch']
    }

    s = ''
    if status:
        s = set_green('ok: ')
    else:
        s = set_red('fatal: ')

    s = s + f'[{command}] => (item="local": {local}, "remote":{remote})'

    s = color_reset(s)

    return s


def repo_create_execute(repo, send_rev):
    path = repo.get('path')
    data = repo.get('data')
    item = Repo.repo(path, data)
    send_rev.send({
        'kind': 'repo',
        'path': path,
        'data': {
            'commands': data['commands'],
            'local': data['local'],
            'remote': {
                'name': data['remote']['name'],
                'branch': data['remote']['branch']
            }
        },
        'result': item.execute()
    })


def result_show(mode, result_list):
    ok_count = 0
    fail_count = 0
    for result in result_list:
        print(view_task_line(result))
        # print(view_repo_line(result))
        # print(result['path'])
        for command, status in result['result'].items():
            print(view_repo_line(result['data'], command, status))
            if status:
                ok_count = ok_count + 1
            else:
                fail_count = fail_count + 1
            # print(command, status)
        print()

    print(view_recap_line())

    s = set_green(mode) if fail_count == 0 else set_red(mode)
    s = color_reset(s)
    s = s + '                  : '
    s = s + set_green(f'ok={ok_count}')
    s = color_reset(s) + '    '
    if fail_count != 0:
        s = s + set_red(f'fail={fail_count}')
    else:
        s = s + 'fail=0'
    print(s)


def main(mode):
    config_file_path = get_config_file_path()
    with open(config_file_path) as f:
        config = toml.load(f)

    print(view_play_line(config_file_path))
    print()

    # print(json.dumps(config, indent=4, sort_keys=True, separators=(',', ': ')))
    # exit()

    for repo in config.get(mode).get('repo'):
        _, _, exception = Repo.is_valid_args(repo.get('path'), repo.get('data'))
        if exception:
            raise exception

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
    result_show(mode, result_list)
    # for res in result_list:
    #     print(res)


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
