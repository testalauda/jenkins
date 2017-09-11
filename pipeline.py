# -*- coding: UTF-8 -*-
import json
import logging
from time import time, sleep

import requests
from brewmaster.run import case
import build_data
import pipeline_data
import settings
from CLaaS.sync_image import create_sync_config, delete_sync_config
from utils import get_registry_info, retry, get_events, get_repo, create_private_build, delete_private_build, get_region_data

logger = logging.getLogger()
REGIONS = settings.SERVICE_CLAAS_REGION
headers = {
    "Authorization": "Token " + settings.API_TOKEN,
    'User-Agent': 'rubick/v1.0',
    'Content-Type': "application/json"
}
registry_uuid = get_registry_info().get("registry_uuid", None)
registry_url = get_registry_info().get("registry_url", None)


@retry(times=settings.RETRY_TIMES)
def create_pipeline(pipeline_name, data):
    delete_pipeline(pipeline_name)
    time1 = time()
    url = "{}pipelines/{}/config".format(settings.API_URL, settings.CLAAS_NAMESPACE)
    print data, type(data)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r.text
    if r.status_code != 201:
        return {"success":False, "total": "create pipeline return code error: {}, error text:{}".format(r.status_code,r.text)}
    if not get_events(pipeline_name, "create"):
        return {"success": False, "total": "this action do not have events"}
    result = json.loads(r.text)
    if "name" in result and result['name'] == pipeline_name:
        time2 = time()
        return {"success": True, "total": time2-time1}
    else:
        return {"success":False, "totol": "r.text is {}, r.status_code is {}".format(r.text, r.status_code)}
    
 def create_pipeline(pipeline_name, data):
    delete_pipeline(pipeline_name)
    time1 = time()
    url = "{}pipelines/{}/config".format(settings.API_URL, settings.CLAAS_NAMESPACE)
    print data, type(data)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r.text
    if r.status_code != 201:
        return {"success":False, "total": "create pipeline return code error: {}, error text:{}".format(r.status_code,r.text)}
    if not get_events(pipeline_name, "create"):
        return {"success": False, "total": "this action do not have events"}
    result = json.loads(r.text)
    if "name" in result and result['name'] == pipeline_name:
        time2 = time()
        return {"success": True, "total": time2-time1}
    else:
        return {"success":False, "totol": "r.text is {}, r.status_code is {}".format(r.text, r.status_code)}


@retry(times=settings.RETRY_TIMES)
def get_pipeline(pipeline_name):
    time1 = time()
    url = "{}pipelines/{}/config/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, pipeline_name)
    r = requests.get(url, headers=headers)
    if r.status_code !=200:
        return {"success":False, "total": "get pipeline return code error: {}, error text:{}".format(r.status_code,r.text)}
    result = json.loads(r.text)
    if "name" in result and result['name'] == pipeline_name:
        time2 = time()
        return {"success": True, "total": time2-time1}
    else:
        return {"success":False, "totol": "r.text is {}, r.status_code is {}".format(r.text, r.status_code)}


@retry(times=settings.RETRY_TIMES)
def get_pipeline_list():
    time1 = time()
    url = "{}pipelines/{}/config".format(settings.API_URL, settings.CLAAS_NAMESPACE)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return {"success":False, "total": "get pipeline list return code error: {}, error text:{}".format(r.status_code,r.text)}
    time2 = time()
    return {"success": True, "total": time2 - time1}


@retry(times=settings.RETRY_TIMES)
def update_pipeline(pipeline_name, payload):
    time1 = time()
    url = "{}pipelines/{}/config/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, pipeline_name)
    r = requests.put(url, data=json.dumps(payload), headers=headers)
    if r.status_code != 204:
        return {"success":False, "total": "update template return code error: {},error text:{}".format(r.status_code, r.text)}
    if not get_events(pipeline_name, "update"):
        return {"success": False, "total": "this action do not have events"}
    r = requests.get(url, headers=headers)
    if "description" in json.loads(r.text):
        description = json.loads(r.text)['description']
        if description == "update pipeline":
            time2 = time()
            return {
                "success": True,
                "total": time2 - time1
            }
        else:
            return {"success": False, "total": "update message error,r.text is {}".format(r.text)}
    else:
        return {"success": False, "total": "description not in template, r.text is {}".format(r.text)}


@retry(times=settings.RETRY_TIMES)
def trigger(pipeline_name):
    get_repo_url = "{}registries/{}/{}/repositories/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE,
                                                               settings.PRIVATE_REGISTRY, get_repo().get("service_repo", "houchao-test"))
    r = requests.get(get_repo_url, headers=headers)
    if r.status_code != 200:
        return {"success": False,
                "total": "get repositories return code error: {}, error text:{}".format(r.status_code, r.text)}
    repo_detail = json.loads(r.text)
    registry_uuid = repo_detail['registry']['uuid']
    repo_uuid = repo_detail['uuid']
    url = "{}pipelines/{}/history/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, pipeline_name)
    payload = {
        "namespace": settings.CLAAS_NAMESPACE,
        "pipeline": pipeline_name,
        "trigger": "repository",
        "data":{
            "image_tag": "latest",
            "registry_uuid": registry_uuid,
            "registry": settings.PRIVATE_REGISTRY,
            "repository": "{}/{}".format(settings.CLAAS_NAMESPACE, get_repo().get("service_repo", "houchao-test")),
            "repository_uuid": repo_uuid,
            "type": "repository"
        }
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        return {"success":False, "total": "trigger pipeline return code error: {}, error text:{}".format(r.status_code, r.text)}
    uuid = json.loads(r.text)["uuid"]
    if not get_events(uuid, "create"):
        return {"success": False, "total": "this action do not have events"}
    return {
        "success": True,
        "uuid": uuid
    }

@retry(times=settings.RETRY_TIMES)
def trigger_build_pipeline(pipeline_name,build_name):
    time1 = time()
    get_build_url = "{}private-build-configs/{}/{}/".format(settings.API_URL, settings.CLAAS_NAMESPACE,
                                                            build_name)

    r = requests.get(get_build_url, headers=headers)
    if r.status_code != 200:
        return {"success": False,
                "total": "get build config return code error: {}, error text:{}".format(r.status_code, r.text)}
    build_detail = json.loads(r.text)
    build_uuid = build_detail['config_id']
    url = "{}pipelines/{}/history/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, pipeline_name)
    payload = {
        "namespace": settings.CLAAS_NAMESPACE,
        "pipeline": pipeline_name,
        "trigger": "build",
        "data": {
            "build_config_uuid": build_uuid,
            "build_config_name": build_name,
            "type": "build",
            "active": True
        }
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        return {"success": False,
                "total": "trigger pipeline return code error: {}, error text:{}".format(r.status_code, r.text)}
    uuid = json.loads(r.text)["uuid"]
    if not get_events(uuid, "create"):
        return {"success": False, "total": "this action do not have events"}
    resultSet = get_pipeline_info(pipeline_name, uuid)
    if resultSet['success']:
        return {"success": True, "total": time() - time1}
    else:
        return resultSet


@retry(times=settings.RETRY_TIMES)
def trigger_pipeline(pipeline_name):
    time1 = time()
    ret = trigger(pipeline_name)
    if ret['success']:
        resultSet = get_pipeline_info(pipeline_name, ret['uuid'])
        time2 = time()
        if resultSet['success']:
            return {"success":True, "total": time2-time1}
        else:
            return resultSet
    else:
        return ret


@retry(times=settings.RETRY_TIMES)
def get_pipeline_info(pipeline_name, uuid):
    url = "{}pipelines/{}/history/{}/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, pipeline_name, uuid)
    cnt = 0
    while cnt < 600:
        # print cnt
        cnt = cnt + 1
        r = requests.get(url, headers=headers)
        if r.status_code < 200 or r.status_code >= 300:
            errmsg = "Failed in calling jakiro API: get trigger pipeline({}),error text({})"\
                .format(r.status_code, r.text)
            return {"success": False, "code": r.status_code, "message": errmsg}
        status = json.loads(r.text)['status']
        if status == 'completed':
            return {"success": True, "status": status}
        elif status == 'failed':
            return {"success": False, "status": status,
                    "message": "get trigger pipeline info : the pipeline is failed. pipeline id is {}".format(uuid)}
        sleep(3)

    return {"success": False, "status": status,
            "message": "Timeout in pipeline"}

@retry(times=settings.RETRY_TIMES)
def delete_pipeline(pipeline_name):
    time1 = time()
    url = "{}pipelines/{}/config/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, pipeline_name)
    r = requests.delete(url, headers=headers)
    if r.status_code != 204:
        return {"success":False, "total": "delete pipeline return code error: {},error text:{}".format(r.status_code, r.text)}
    if not get_events(pipeline_name, "destroy"):
        return {"success": False, "total": "this action do not have events"}
    time2 = time()
    return {"success": True, "total": time2-time0}


@retry(times=settings.RETRY_TIMES)
def stop_pipeline(pipeline_name):
    time1 = time()
    ret = trigger(pipeline_name)
    if ret['success']:
        url = "{}pipelines/{}/history/{}/{}/stop/".format(settings.API_URL, settings.CLAAS_NAMESPACE, pipeline_name, ret['uuid'])
        print url
        r = requests.put(url, headers=headers)
        print r
        if r.status_code != 204:
            return {"success": False, "status": r.status_code,
                    "message": "stop pipeline info failed. pipeline id is {}, message:{}".format(ret['uuid'], r.text)}
        if not get_events(ret['uuid'], "stop"):
            return {"success": False, "total": "this action do not have events"}
        resultSet = get_pipeline_info(pipeline_name, ret['uuid'])
        if resultSet["status"] == "failed":
            return {"success": True, "total": time()-time1, "uuid": ret['uuid']}
        else:
            return resultSet
    else:
        return ret


@retry(times=settings.RETRY_TIMES)
def delete_pipeline_history(pipeline_name, uuid):
    time1 = time()
    url = "{}pipelines/{}/history/{}/{}/".format(settings.API_URL, settings.CLAAS_NAMESPACE, pipeline_name, uuid)
    r = requests.delete(url, headers=headers)
    if r.status_code != 204:
        return {"success": False, "message": "delete failed:r.status_code is {}, r.text is {}".format(r.status_code, r.text)}
    if not get_events(uuid, "destroy"):
        return {"success": False, "total": "this action do not have events"}
    time2 = time()
    return {"success": True, "total": time2 - time1}

class PipelineTest(object):

    def pipeline_set_up(self):

        if 'pipeline' in ((self.region_data)['data']['features']['service']['features']):
            self.pipeline_name = "e2e-test{}".format(settings.SERVICE_CLAAS_REGION[0])
            self.create_nomal_data = pipeline_data.PipelineData(self.pipeline_name, "this is a description")
            self.update_nomal_data = pipeline_data.PipelineData(self.pipeline_name, "update pipeline")

            self.build_name = "e2e-build-config{}".format(settings.SERVICE_CLAAS_REGION[0])
            self.build_pipeline_name = "e2e-build-test{}".format(settings.SERVICE_CLAAS_REGION[0])
            svn_repo = settings.SVN_REPO + "呵呵"
            chinese_url_data = build_data.BuildCIData(self.build_name, "SIMPLE_SVN",
                                                      svn_repo,
                                                      code_repo_type="DIR", code_repo_type_value='/')
            create_private_build(chinese_url_data.nomal_build_data())
            self.build_pipeline_data = pipeline_data.PipelineData(self.build_pipeline_name, "this is a description",
                                                                  build_name=self.build_name)

            self.sync_config_name = "e2e-sync_config{}".format(settings.SERVICE_CLAAS_REGION[0])
            self.sync_pipeline_name = "e2e-sync_test{}".format(settings.SERVICE_CLAAS_REGION[0])
            self.repo_name = "houchao-test"
            self.username = "{}/{}".format(settings.CLAAS_NAMESPACE, settings.NAMESPACE)
            create_sync_config(self.sync_config_name, self.repo_name, self.username)
            self.sync_pipeline_data = pipeline_data.PipelineData(self.sync_pipeline_name, "this is a description",
                                                                 sync_config_name=self.sync_config_name)

    def pipeline_tear_down(self):
        if 'pipeline' in ((self.region_data)['data']['features']['service']['features']):
            delete_pipeline(self.pipeline_name)
            delete_private_build(self.build_name)
            delete_pipeline(self.build_pipeline_name)
            delete_sync_config(self.sync_config_name)
            delete_pipeline(self.sync_pipeline_name)

    @case
    def pipeline_test__pipeline(self):

        if 'pipeline' in ((self.region_data)['data']['features']['service']['features']):
            ret1 = create_pipeline(self.pipeline_name, self.create_nomal_data.create_pipeline_data())
            self.assert_successful(ret1)
            ret2 = get_pipeline_list()
            self.assert_successful(ret2)
            ret3 = get_pipeline(self.pipeline_name)
            self.assert_successful(ret3)
            ret6 = stop_pipeline(self.pipeline_name)
            self.assert_successful(ret6)

            ret7 = delete_pipeline_history(self.pipeline_name, ret6['uuid'])
            self.assert_successful(ret7)
            ret4 = update_pipeline(self.pipeline_name, self.update_nomal_data.update_pipeline_data())
            self.assert_successful(ret4)
            ret5 = trigger_pipeline(self.pipeline_name)
            self.assert_successful(ret5)
            ret8 = delete_pipeline(self.pipeline_name)
            self.assert_successful(ret8)
            obj = {
                "success": True,
                "create_pipeline": ret1,
                "get_pipeline_list": ret2,
                "get_pipeline": ret3,
                "stop_pipeline": ret6,
                "delete_pipeline_history": ret7,
                "update_pipeline": ret4,
                "trigger_pipeline": ret5,
                "delete_pipeline": ret8
            }
            return obj
        else:
            warning = {"success": True,
                       "message": "No <pipiline> found in region feature, pipeline case not run, please check manually"
                       }
            return warning


    @case
    def build_pipeline_test__pipeline(self):
        if 'pipeline' in ((self.region_data)['data']['features']['service']['features']):
            ret1 = create_pipeline(self.build_pipeline_name, self.build_pipeline_data.build_pipeline_data())
            self.assert_successful(ret1)
            ret2 = get_pipeline_list()
            self.assert_successful(ret2)
            ret3 = get_pipeline(self.build_pipeline_name)
            self.assert_successful(ret3)
            ret5 = trigger_build_pipeline(self.build_pipeline_name, self.build_name)
            self.assert_successful(ret5)
            ret8 = delete_pipeline(self.build_pipeline_name)
            self.assert_successful(ret8)
            obj = {
                "success": True,
                "create_pipeline": ret1,
                "get_pipeline_list": ret2,
                "get_pipeline": ret3,
                "trigger_pipeline": ret5,
                "delete_pipeline": ret8
            }
            return obj
        else:
            warning = {"success": True,
                       "message": "No <pipiline> found in region feature, pipeline case not run, please check manually"
                       }
            return warning


    @case
    def sync_pipeline_test__pipeline(self):
        if 'pipeline' in ((self.region_data)['data']['features']['service']['features']):
            ret1 = create_pipeline(self.sync_pipeline_name, self.sync_pipeline_data.sync_pipeline_data())
            self.assert_successful(ret1)
            ret2 = get_pipeline_list()
            self.assert_successful(ret2)
            ret3 = get_pipeline(self.sync_pipeline_name)
            self.assert_successful(ret3)
            ret5 = trigger_pipeline(self.sync_pipeline_name)
            self.assert_successful(ret5)
            ret8 = delete_pipeline(self.sync_pipeline_name)
            self.assert_successful(ret8)
            obj = {
                "success": True,
                "create_pipeline": ret1,
                "get_pipeline_list": ret2,
                "get_pipeline": ret3,
                "trigger_pipeline": ret5,
                "delete_pipeline": ret8
            }
            return obj
        else:
            warning = {"success": True,
                       "message": "No <pipiline> found in region feature, pipeline case not run, please check manually"
                       }
            return warning
       def test:
        if :
            
        else:
            print "ssf"









