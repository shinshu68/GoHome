import os
import json
import toml

config_file = ''
if os.getenv('XDG_CONFIG_HOME'):
    config_file = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'prepost', 'config.toml')
else:
    config_file = os.path.join(os.getenv('HOME'), '.config', 'prepost', 'config.toml')

if not os.path.exists(config_file):
    print('config file is not exists.')

with open(config_file) as f:
    config = toml.load(f)
    print(json.dumps(config, indent=4, sort_keys=True, separators=(',', ': ')))
