# -*- coding:utf-8 -*-
# AUTHOR: SUN
from time import sleep

from schedule import run_pending

import scheduler

if __name__ == '__main__':
    while True:
        run_pending()
        sleep(1)
