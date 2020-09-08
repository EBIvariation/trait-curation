import yaml

try:
    file = open('config.yaml', 'r')
    config = yaml.load(file, Loader=yaml.FullLoader)
except FileNotFoundError as e:
    print('Config file not found! Make sure you have config.yaml in the project directory')
    raise e

DEBUG = True

DATABASES = {'default': config['DATABASES']['POSTGRES']}
