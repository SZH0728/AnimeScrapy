# -*- coding:utf-8 -*-
# AUTHOR: Sun

from os import name, getenv

def set_constant[T](env_name: str, default: T) -> T:
    if name =='nt':
        return default
    elif name == 'posix':
        return getenv(env_name)
    else:
        raise Exception('Unsupported OS')

USERNAME = set_constant('USERNAME', 'root')
PASSWORD = set_constant('PASSWORD', '123456')
HOST = set_constant('HOST', 'localhost')
PORT = set_constant('PORT', '3306')

LOG_PATH = set_constant('LOG_PATH', 'log.txt')
PICTURE_PATH = set_constant('PICTURE_PATH', './examples')

if __name__ == '__main__':
    pass
