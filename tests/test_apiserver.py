# -*- coding: utf-8 -*-

"""
    tests.apiserver
    ~~~~~~~~~~~~

    Tests cobra.api

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""

import requests
import json
import multiprocessing
import time
import os
import shutil
import socket
from cobra.config import project_directory
from cobra.api import start

p = multiprocessing.Process(target=start, args=('127.0.0.1', 5000, False))
p.start()
time.sleep(1)

config_path = os.path.join(project_directory, 'config')
template_path = os.path.join(project_directory, 'config.template')
shutil.copyfile(template_path, config_path)


def test_add_job():
    url = "http://127.0.0.1:5000/api/add"
    post_data = {
        "key": "your_secret_key",
        "target": ["https://github.com/shadowsocks/shadowsocks.git"],
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)
    assert "1001" in re.text
    assert "Add scan job successfully" in re.text
    assert "sid" in re.text


def test_job_status():
    url = "http://127.0.0.1:5000/api/status"
    post_data = {
        "key": "your_secret_key",
        "sid": 24,
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)
    assert "1001" in re.text
    assert "msg" in re.text
    assert "sid" in re.text
    assert "status" in re.text
    assert "report" in re.text


def test_close_api():
    os.remove(config_path)
    p.terminate()
    p.join()

    # wait for scan process
    while True:
        cobra_process = os.popen('ps aux | grep test_apiserver.py').read()
        cobra_process_num = len(cobra_process.strip().split('\n'))
        if cobra_process_num <= 3:
            # grep test_apiserver.py
            # sh -c ps aux | grep test_apiserver.py
            # python test_apiserver.py
            break
        time.sleep(1)

    # whether port 5000 is closed
    s = socket.socket()
    s.settimeout(0.5)
    try:
        assert s.connect_ex(('localhost', 5000)) != 0
    finally:
        s.close()

    assert not os.path.exists(config_path)
