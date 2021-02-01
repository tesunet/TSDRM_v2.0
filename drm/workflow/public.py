import re
from ast import literal_eval
from lxml import etree
import base64
import requests
import json

from celery.app.control import Control
from TSDRM.celery import app


def revoke_p_task(pr_id):
    """
    中止指定流程所有taskid：name=faconstor.tasks.exec_process的最新任务中止
    return status{bool}: 1 成功 2 失败 0 任务不存在
    """
    status = 0
    try:
        task_url = "http://127.0.0.1:5555/api/tasks"

        try:
            task_json_info = requests.get(task_url).text
        except:
            status = 2
        else:
            task_dict_info = json.loads(task_json_info)
            c_control = Control(app=app)

            for key, value in task_dict_info.items():
                try:
                    task_process_id = value["args"][1:-1].split(',')[0][1:-1]
                except:
                    task_process_id = ""
                # 终止指定流程的异步任务
                if task_process_id == pr_id and value["name"] == "drm.tasks.run_workflow":
                    task_id = key
                    print(key)
                    c_control.revoke(str(task_id), terminate=True)
                    status = 1
    except Exception as e:
        print(e)
        status = 2
    return status
