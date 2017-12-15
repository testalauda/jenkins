# coding=utf-8
from time import sleep, time
import logging
import settings
import json
import requests
from utils import is_deploying, apicall_claas_service, get_service_info, can_visit, exec_feature,\
    get_service_result, get_events, retry

logger = logging.getLogger()
REGIONS = settings.SERVICE_CLAAS_REGION
headers = {
    "Authorization": "Token " + settings.API_TOKEN,
    'content-type': 'application/json'
}

@retry(times=settings.RETRY_TIMES)
def create_service(name, payload, service_detail='Hello', region='STAGING'):
    delete_app(name, region)
    print "create claas service"
    logger.info(region + " Start creating service")

    time1 = time()
    print payload
    (code, text) = apicall_claas_service('create_service', name, payload)
    logger.info("apicall returns (%d, %s)" % (code, text))
    print ("apicall returns (%d, %s)" % (code, text))
    if code < 200 or code >= 300:
        msg = "Error in calling create Claas API {}:{}".format(code, text)
        return {"success": False, "total": msg}
    if not get_events(name, "create"):
        return {"success": False, "total": "this action do not have events"}

    # test if at least 1 instance is running
    target = {"status": "Running", "text": service_detail}
    isdeploying = is_deploying(name, target, 200, settings.CLAAS_NAMESPACE)
    time2 = time()
    logger.info(region + " is_deploying check use {}s".format(time2 - time1))
    if isdeploying:
        (code, text, obj) = get_service_info(name, 0, settings.CLAAS_NAMESPACE)
        if 'current_status' in obj:
            if obj['current_status'].find('Error') >= 0:
                return {"success": False, "total": "create service {} status is Error".format(name)}
            if "instance_ports" in json.loads(text) and len(json.loads(text)['instance_ports']):
                if "endpoint_type" in json.loads(text)['instance_ports'][0] and json.loads(text)['instance_ports'][0]['endpoint_type'] == "internal-endpoint":
                    (code, html) = get_service_result(json.loads(text)["instance_ports"][0]["default_domain"])
                    if code > 300 or code < 200:
                        return {"success": True, "total": time2 - time1}
                    else:
                        return {"success": False, "total": "internal haproxy service should not can visit"}
            flag = can_visit(target, text)
            if not flag and obj['current_status'] == 'Running':
                return {"success": False, "total": "create service {} can not visit".format(name)}
        msg = "Timeout in creating {} service".format(name)
        return {"success": False, "total": msg}
    logger.info(region + " create use {}s".format(time2 - time1))

    return {
        "success": True,
        "total": time2 - time1
    }


@retry(times=settings.RETRY_TIMES)
def delete_app(name, region_name='STAGING'):
    logger.info(region_name + " start deleting {}".format(name))

    time1 = time()
    (code, text) = apicall_claas_service('delete_service', name)
    logger.info(region_name + " apicall returns (%d, %s)" % (code, text))
    if code < 200 or code >= 300:
        msg = "Error in calling delete API {}:{}".format(code, text)
        return {"success": False, "total": msg}

    time2 = time()
    logger.info(region_name + " total deletion uses %f seconds"
                % (time2 - time1))
    sleep(10)
    if not get_events(name, "destroy"):
        return {"success": False, "total": "this action do not have events"}
    obj = {
        "success": True,
        "total": time2 - time1
    }
    return obj

#验证服务的volume id or type
def verify_volumes(service_name, volume_id, app_name=''):
    print "===========get service detail to verify volumes============"
    time1 = time()
    (code, service_detail) = apicall_claas_service('get_service', service_name, app_name=app_name)
    if code != 200:
        return {"success": False,
                "total": "get service failed, error code is {}.error message is ".format(code, service_detail)}
    #判断服务的存储卷类型
    if volume_id != json.loads(service_detail)['volumes'][0]['volume_id']:
        return {"success": False, "total": "service volume_id is {},inspect {}".format(
            json.loads(service_detail)['volumes'][0]['volume_id'], volume_id)}
    time2 =time()
    return {"success": True, "total": time2 - time1}

#获取服务的日志文件
def get_logfile(service_name, app_name=''):
    print "=============get log file===================="
    url = "{}services/{}/{}/logs/sources?service_name={}&namespace={}&application={}".\
        format(settings.API_URL,settings.CLAAS_NAMESPACE, service_name,service_name, settings.CLAAS_NAMESPACE,app_name)
    r = requests.get(url,headers=headers)
    if r.status_code != 200:
        return {"success": False,
                "total": "get service log file failed, error code is {}.error message is ".format(r.status_code,
                                                                                                  r.text)}
    content = json.loads(r.text)
    for i in range(0, len(content)):
        if "txt" in content[i]:
            return get_logs(service_name, log_source=content[i], app_name=app_name)
    return {"success": False, "total": "logfile not found,log source is {}".format(content)}


@retry(times=settings.RETRY_TIMES)
def get_metrics(name, app_name=''):
    logger.info(" start get service metrics")
    print "get_metrics()"

    time1 = time()
    (code, service_detail) = apicall_claas_service('get_service', name, app_name=app_name)
    if code < 200 or code > 300:
        msg = "Error in get_instances API {}:{}".format(code,
                                                        service_detail)
        return {"success": False, "total": msg}

    cnt = 0
    isdeploying = True
    service_id = json.loads(service_detail).get("uuid",None)
    text = ''
    while cnt < 200 and isdeploying:
        cnt = cnt + 1
        tm_end = int(time())
        tm_start = tm_end-1800

        isdeploying = False
        url = settings.API_URL.replace("v1", "v2") + "monitor/" + settings.CLAAS_NAMESPACE + \
              "/metrics/query/?q=avg:service.mem.utilization{service_id="+ service_id + "}by{instance_id}&start=" \
              + str(tm_start) + "&end=" + str(tm_end) + "&namespace=" + settings.CLAAS_NAMESPACE
        r = requests.get(url, headers=headers)
        logger.info(" get service metrics {} {} '{}'"
                    .format(name, r.status_code, r.text))
        if r.status_code >= 300 or json.loads(r.text) == []:
            isdeploying = True
            sleep(2)
            continue
        obj = json.loads(r.text)
        print "metrics is {}".format(obj)
        if obj[0].get('dps', {}) == {}:
            isdeploying = True
            sleep(2)
            continue

    if r.status_code >= 300:
        msg = "Failed in getting metrics , return code:{}, text:{}".format(r.status_code, r.text)
        return {"success": False, "total": msg}
    if json.loads(r.text) == []:
        msg = "Failed in getting metrics , text is null"
        return {"success": False, "total": msg}
    if json.loads(r.text)[0]['dps'] == {}:
        msg = "Failed in getting metrics , text is {}"
        return {"success": False, "total": msg}
    time2 = time()
    logger.info(" ==> Getting metrics uses {}s"
                .format(time2 - time1))
    obj = {
        "success": True,
        "total": time2 - time1
    }
    return obj


@retry(times=settings.RETRY_TIMES)
def get_logs(name, log_source='alauda_stdout', app_name=''):
    logger.info(" start get service logs")
    print "get_logs()"

    time1 = time()

    cnt = 0
    is_deploying = True
    logs_code = 200
    logs_text = ''
    while cnt < 200 and is_deploying:
        cnt = cnt + 1
        tm_end = int(time())
        tm_start = tm_end-604800
        # app_name为空的话是服务的日志  app_name有值则为应用内部服务的日志
        interval_time = "/logs/?limit=1000&start_time=%s&log_source=%s&end_time=%s" % (tm_start,log_source,tm_end)
        is_deploying = False
        instance_logs = name + interval_time
        print "instance logs: "
        url = "{}/services/{}/{}&application={}".format(settings.API_URL, settings.CLAAS_NAMESPACE, instance_logs, app_name)
        print "instance logs:{} ".format(url)
        r = requests.get(url, headers=headers)
        logs_text = r.text
        logs_code = r.status_code
        print (logs_code, logs_text)
        if logs_code < 200 or logs_code > 300:
            is_deploying = True
            sleep(2)
        if logs_text == '""' or logs_text == '[]':
            is_deploying = True
            sleep(5)
    if logs_code < 200 or logs_code > 300:
        msg = "Failed in getting logs code:{} ,text:{}".format(logs_code, logs_text)
        return {"success": False, "total": msg}
    if logs_text == '""' or logs_text == '[]':
        return {"success": False, "total": "log is null"}

    time2 = time()
    logger.info(" total getting logs uses {}s"
                .format(time2 - time1))
    obj = {
        "success": True,
        "total": time2 - time1
    }
    print "get logs success"
    return obj


def start_app(name, num):
    logger.info(" start service")
    print "start_app()"

    time1 = time()
    (code, text) = apicall_claas_service('start_service', name)
    logger.info(" apicall returns (%d, %s)" % (code, text))
    if code < 200 or code >= 300:
        msg = "Error in calling start API {}:{}".format(code, text)
        return {"success": False, "total": msg}

    target = {"status": "Running", "num": num}
    if not get_events(name, "start"):
        return {"success": False, "total": "this action do not have events"}
    isdeploying = is_deploying(name, target, 180, settings.CLAAS_NAMESPACE)
    time2 = time()
    if isdeploying:
        (code, text, obj) = get_service_info(name, 0, settings.CLAAS_NAMESPACE)
        if 'current_status' in obj:
            if obj['current_status'].find('Error') >= 0:
                return {"success": False, "total": "restart {} service status is Error".format(name)}
        return {"success": False, "total": "Timeout in starting {}".format(name)}

    logger.info(" ==> Starting service uses {}s"
                .format(time2 - time1))
    obj = {
        "success": True,
        "total": time2 - time1
    }
    return obj


def stop_app(name):
    logger.info(" Stopping service")
    print "stop_app()"

    time1 = time()
    (code, text) = apicall_claas_service('stop_service', name)
    logger.info(" apicall returns (%d, %s)" % (code, text))
    if code < 200 or code >= 300:
        msg = "Error in calling stop API {}:{}".format(code, text)
        return {"success": False, "total": msg}
    if not get_events(name, "stop"):
        return {"success": False, "total": "this action do not have events"}
    target = {"status": "Stopped", "num": 0}
    isdeploying = is_deploying(name, target, 120, settings.CLAAS_NAMESPACE)
    time2 = time()
    if isdeploying:
        return {"success": False, "total": "Timeout in stopping {}".format(name)}

    logger.info(" ==> Stopping service uses {}s"
                .format(time2 - time1))
    obj = {
        "success": True,
        "total": time2 - time1
    }
    return obj


def update_service(name, num, size, service_detail='Hello'):
    print "scale_app()"
    logger.info(" Start scaling service {}".format(name))

    time1 = time()
    payload = {
          # "image_tag": "latest",
          "target_num_instances": num,
          "instance_size": size 
          }
    (code, text) = apicall_claas_service('modify_service', name, payload)
    logger.info(" apicall returns (%d, %s)" % (code, text))
    if code < 200 or code >= 300:
        msg = "Error in calling scale API {}:{}".format(code, text)
        return {"success": False, "total": msg}
    if not get_events(name, "update"):
        return {"success": False, "total": "this action do not have events"}

    target = {"status": "Running", "num": num, "size": size, "text": service_detail}
    isdeploying = is_deploying(name, target, 240, settings.CLAAS_NAMESPACE)
    time2 = time()
    if isdeploying:
        (code, text, obj) = get_service_info(name, 0, settings.CLAAS_NAMESPACE)
        if 'current_status' in obj:
            if obj['current_status'].find('Error') >= 0:
                return {"success": False, "total": "update service {} status is Error".format(name)}
            flag = can_visit(target, text)
            if not flag and obj['current_status'] == 'Running':
                return {"success": False, "total": "update service {} can not visit".format(name)}
        msg = "Timeout in scaling {}".format(name)
        return {"success": False, "total": msg}

    logger.info(" ==> Scaling uses {}s"
                .format(time2 - time1))
    return {
        "success": True,
        "total": time2 - time1
    }


def test_process(data, region, text='Hello', full_data=False):
    print "======= service data payload is ========"
    print data
    app_name = data['service_name']
    test_flag = True

    ret_create = create_service(app_name, data, service_detail=text, region=region)
    if not ret_create["success"]:
        print "create service failed :{}".format(ret_create)
        delete_app(app_name, region)
        return add_to_total_dict(ret_create, app_name)

    logger.info(region +
                " Creating a service %fs finished\n\n"
                % (ret_create["total"]))
    sleep(10)

    ret_metrics = get_metrics(app_name)
    if not ret_metrics['success']:
        test_flag = False
    ret_exec = exec_feature(app_name, region, settings.CLAAS_NAMESPACE)
    if not ret_exec['success']:
        test_flag = False
    
    ret_stop = stop_app(app_name)
    if not ret_stop["success"]:
        delete_app(app_name, region)
        return add_to_total_dict(ret_stop, app_name)

    logger.info(region + " Stop the service %s finished\n\n"
                % ret_stop["total"])
    sleep(10)

    ret_restart = start_app(app_name, num=1)
    if not ret_restart["success"]:
        delete_app(app_name, region)
        return add_to_total_dict(ret_restart, app_name)

    logger.info(region + " Start the service %s finished\n\n"
                % ret_restart["total"])
    sleep(1)
    
    scale_up = update_service(app_name, num=2, size="XS", service_detail=text)
    if not scale_up["success"]:
        delete_app(app_name, region)
        return add_to_total_dict(scale_up, app_name)

    scale_down = update_service(app_name, num=1, size="XS", service_detail=text)
    if not scale_down["success"]:
        delete_app(app_name, region)
        return add_to_total_dict(scale_down, app_name)

    logger.info(region + " Redeploy the service %s finished\n\n"
                % scale_down["total"])

    ret_logs = get_logs(app_name)
    if not ret_logs['success']:
        test_flag = False
    
    logger.info(region + " begin to delete service")
    ret7 = delete_app(app_name, region)
    if not ret7["success"]:
        delete_app(app_name, region)
        return add_to_total_dict(ret7, app_name)

    logger.info(region + " Delete the service %s finished\n\n"
                % ret7["total"])

    if not full_data:
        obj = {
            "success": test_flag,
            "{} create".format(app_name): ret_create["total"],
            "{} get logs".format(app_name): ret_logs["total"],
            "{} get metrics".format(app_name): ret_metrics["total"],
            "{} exec_feature".format(app_name): ret_exec["total"],
            "{} get stop service".format(app_name): ret_stop["total"],
            "{} get restart service".format(app_name): ret_restart["total"],
            "{} scale up service".format(app_name): scale_up["total"],
            "{} scale down service".format(app_name): scale_down["total"],
            "{} delete".format(app_name): ret7["total"],
        }
    else:
        obj = {
            "success": test_flag,
            "{} create".format(app_name): ret_create,
            "{} get logs".format(app_name): ret_logs,
            "{} get metrics".format(app_name): ret_metrics,
            "{} exec_feature".format(app_name): ret_exec,
            "{} get stop service".format(app_name): ret_stop,
            "{} get restart service".format(app_name): ret_restart,
            "{} scale up service".format(app_name): scale_up,
            "{} scale down service".format(app_name): scale_down,
            "{} delete".format(app_name): ret7,
        }

    return obj


