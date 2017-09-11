from time import time, sleep
from utils import get_events, retry, get_region_id
import logging
import settings
import requests
import json
import data
from brewmaster.run import case
from common import create_service, update_service, stop_app, delete_app

logger = logging.getLogger()
REGIONS = settings.SERVICE_CLAAS_REGION
headers = {
    "Authorization": "Token " + settings.API_TOKEN,
    'content-type': 'application/json'
}
region_id = get_region_id().get("region_id", None)


@retry(times=settings.RETRY_TIMES)
def create_alarms(alarm_name, payload):
    delete_alarms(alarm_name)
    time1 = time()
    url = "{}alarms/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE)
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print r
    print r.status_code, r.text
    if r.status_code != 201:
        return {
            "success": False,
            "total": "create alarm return code error: {}, error text:{}"
            .format(r.status_code, r.text),
            'payload': payload, 'url': url
        }
    sleep(5)
    if not get_events(alarm_name, "create"):
        return {"success": False, "total": "this action do not have events"}
    time2 = time()
    return {"success": True, "total": time2-time1, 'payload': payload, 'url': url}


@retry(times=settings.RETRY_TIMES)
def update_alarms(alarm_name, payload):
    time1 = time()
    url = "{}alarms/{}/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, alarm_name)
    print "UPDATE ALARM---"
    print "URL - {}".format(url)
    print "PAYLOAD - \n{}".format(payload)
    r = requests.put(url, data=json.dumps(payload), headers=headers)
    print r
    if r.status_code != 204:
        return {
            "success": False,
            "total": "update alarm return code error: {}, error text:{}".format(r.status_code, r.text),
            'payload': payload, 'url': url
        }
    sleep(1)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return {"success":False, "total": "get alarm return code error: {}, error text:{}".format(r.status_code, r.text)}
    sleep(5)
    if not get_events(alarm_name, "update"):
        return {"success": False, "total": "this action do not have events"}
    if "description" in json.loads(r.text):
        description = json.loads(r.text)['description']
        if description == "update alarm":
            time2 = time()
            return {
                "success": True,
                "total": time2 - time1,
                'payload': payload, 'url': url
            }
        else:
            return {"success": False, "total": "update message error", 'payload': payload, 'url': url}
    else:
        return {"success": False, "total": "description not in alarm", 'payload': payload, 'url': url}


def query_alarm(alarm_name):
    url = "{}alarms/{}/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, alarm_name)
    print "GET ALARMS---"
    print "URL - {}".format(url)
    r = requests.get(url, headers=headers)
    print r
    if r.status_code != 200:
        return {"success":False, "total": "get alarm return code error: {},error text:{}".format(r.status_code, r.text)}

    return {"success": True, "total": r}


@retry(times=settings.RETRY_TIMES)
def get_alarms(alarm_name, res_name):
    time1 = time()
    url = "{}alarms/{}/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, alarm_name)
    print "GET ALARMS---"
    print "URL - {}".format(url)
    r = requests.get(url, headers=headers)
    print r
    if r.status_code != 200:
        return {"success":False, "total": "get alarm return code error: {}, error text:{}".format(r.status_code, r.text)}
    if "resource_name" in json.loads(r.text):
        resource_name = json.loads(r.text)['resource_name']
        print('resource_name: {}'.format(resource_name))
        print('res_name: {}'.format(res_name))
        if resource_name == res_name:
            time2 = time()
            return {
                "success": True,
                "total": time2 - time1
            }
        else:
            return {"success": False, "total": "{} not in alarm".format(res_name)}
    else:
        return {"success": False, "total": "resource_name[{}] not in alarm".format(alarm_name)}


@retry(times=settings.RETRY_TIMES)
def delete_alarms(alarm_name):
    time1 = time()
    url = "{}alarms/{}/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, alarm_name)
    print "DELETE ALARM---"
    print "URL - {}".format(url)
    r = requests.delete(url, headers=headers)
    print r
    if r.status_code != 204:
        return {
            "success": False,
            "total": "delete alarm return code error: {}, error text:{}".format(
                r.status_code, r.text
            )
        }
    sleep(5)
    if not get_events(alarm_name, "destroy"):
        return {"success": False, "total": "this action do not have events"}
    time2 = time()
    return {"success": True, "total": time2-time1}


def get_service_info(service_name):
    url = "{}services/{}/{}/".format(settings.API_URL, settings.CLAAS_NAMESPACE, service_name)
    print "GET SERVICE STATE---"
    print "URL - {}".format(url)
    r = requests.get(url, headers=headers)
    print r
    if r.status_code != 200:
        return {"success": False, "total": "get service state return code error: {}, error text:{}".format(r.status_code, r.text)}

    return {"success": True, "total": r}


class AlarmTest(object):
    def alarm_set_up(self):
        self.create_alarm_name = "e2e-alarm-test{}".format(settings.SERVICE_CLAAS_REGION[0])
        self.create_service_name = "e2e-alarm-test-service{}".format(settings.SERVICE_CLAAS_REGION[0])
        self.create_alarm_state_name = "e2e-alarm-state-test{}".format(settings.SERVICE_CLAAS_REGION[0])
        self.app_region = REGIONS[0]
        self.serviceData = data.ServiceData(self.create_service_name, settings.NAMESPACE, self.app_region)

    def alarm_tear_down(self):
        delete_alarms(self.create_alarm_name)
        delete_alarms(self.create_alarm_state_name)
        delete_app(self.create_service_name)

    @case
    def create_alarm__alarms(self):
        payload = [{
            "alarm_actions": {"notifications": [settings.SERVICE_CLAAS_REGION[0]]},
            "resource_name": settings.SERVICE_CLAAS_REGION[0],
            "metric_name": "region-nodes-count",
            "evaluation_periods": 1,
            "description": "",
            "period": 60,
            "actions_enabled": True,
            "dimensions": [],
            "statistic": "Average",
            "threshold": 5,
            "threshold_display": 5,
            "comparison_operator": "GreaterThanOrEqualToThreshold",
            "resource_type": "REGION",
            "resource_uuid": region_id,
            "name": self.create_alarm_name,
        }]
        ret = create_alarms(self.create_alarm_name, payload)
        self.assert_successful(ret)

        payload = {
            "alarm_actions": {"notifications": [settings.SERVICE_CLAAS_REGION[0]]},
            "resource_name": settings.SERVICE_CLAAS_REGION[0],
            "metric_name": "region-nodes-count",
            "evaluation_periods": 1,
            "description": "update alarm",
            "namespace": settings.CLAAS_NAMESPACE,
            "period": 60,
            "actions_enabled": True,
            "dimensions": [],
            "statistic": "Average",
            "threshold": 3,
            "threshold_display": 3,
            "comparison_operator": "GreaterThanOrEqualToThreshold",
            "resource_type": "REGION",
            "resource_uuid": region_id,
            "name": self.create_alarm_name,
        }
        ret = update_alarms(self.create_alarm_name, payload)
        print 'Update alarm result {}'.format(ret)
        self.assert_successful(ret)

        ret = get_alarms(self.create_alarm_name, self.app_region)
        self.assert_successful(ret)

        ret = delete_alarms(self.create_alarm_name)
        self.assert_successful(ret)


    #@case
    def alarm_state__alarms(self):
        ''' test alarm state:  INSUFFICIENT_DATA, OK, ALARM, OUT_OF_OPERATION '''

        # step1: create one service
        # step2: create one alarm to monitor the service, set "metric_name" & "threshold"... to get 'OK' state of alarm
        # step3: update service to get 'ALARM' state of alarm
        # step4: stop service to get 'INSUFFICIENT_DATA' state of alarm
        # step5: delete service to get 'OUT_OF_OPERATION' state of alarm

        ret = create_service(self.create_service_name,
                             self.serviceData.ha_heathy_check_service(), region=self.app_region)
        self.assert_successful(ret)

        ret = get_service_info(self.create_service_name)
        self.assert_successful(ret)
        content = json.loads(ret["total"].content)

        payload = [{
            "alarm_actions": {"notifications": [settings.SERVICE_CLAAS_REGION[0]]},
            "resource_name": self.create_service_name,
            "metric_name": "custom_health_check_healthy_instances",
            "evaluation_periods": 1,
            "description": "",
            "period": 60,
            "actions_enabled": True,
            "dimensions": [],
            "statistic": "Average",
            "threshold": 2,
            "threshold_display": 2,
            "space_name": settings.SPACE_NAME,
            "comparison_operator": "GreaterThanOrEqualToThreshold",
            "resource_type": "SERVICE",
            "resource_uuid": content["uuid"],
            "name": self.create_alarm_state_name,
        }]
        print('payload: {}'.format(payload))
        ret = create_alarms(self.create_alarm_state_name, payload)
        self.assert_successful(ret)

        ret = get_alarms(self.create_alarm_state_name, self.create_service_name)
        self.assert_successful(ret)

        ret = query_alarm(self.create_alarm_state_name)
        self.assert_successful(ret)
        content = json.loads(ret['total'].content)
        if content["state_value"] == 'OK':
            self.assert_successful({"success": True, "total": '{} state is OK'.format(self.create_alarm_state_name)})
        else:
            self.assert_successful({"success": False, "total": '{} state is {}, should be OK'
                                   .format(self.create_alarm_state_name, content["state_value"])})

        ret = update_service(self.create_service_name, 2, 'XXS')
        self.assert_successful(ret)

        sleep(300)
        ret = query_alarm(self.create_alarm_state_name)
        self.assert_successful(ret)
        content = json.loads(ret['total'].content)
        if content["state_value"] == 'ALARM':
            self.assert_successful({"success": True, "total": '{} state is ALARM'.format(self.create_alarm_state_name)})
        else:
            self.assert_successful({"success": False, "total": '{} state is {}, should be ALARM'
                                   .format(self.create_alarm_state_name, content["state_value"])})

        ret = stop_app(self.create_service_name)
        self.assert_successful(ret)

        sleep(300)
        ret = query_alarm(self.create_alarm_state_name)
        self.assert_successful(ret)
        content = json.loads(ret['total'].content)
        if content["state_value"] == 'INSUFFICIENT_DATA':
            self.assert_successful({"success": True, "total": '{} state is INSUFFICIENT_DATA'.format(self.create_alarm_state_name)})
        else:
            self.assert_successful({"success": False, "total": '{} state is {}, should be INSUFFICIENT_DATA'
                                   .format(self.create_alarm_state_name, content["state_value"])})

        ret = delete_app(self.create_service_name, self.app_region)
        self.assert_successful(ret)

        sleep(120)
        ret = query_alarm(self.create_alarm_state_name)
        self.assert_successful(ret)
        content = json.loads(ret['total'].content)
        if content["state_value"] == 'OUT_OF_OPERATION':
            self.assert_successful({"success": True, "total": '{} state is OUT_OF_OPERATION'.format(self.create_alarm_state_name)})
        else:
            self.assert_successful({"success": False, "total": '{} state is {}, should be OUT_OF_OPERATION'
                                   .format(self.create_alarm_state_name, content["state_value"])})

        ret = delete_alarms(self.create_alarm_state_name)
        self.assert_successful(ret)
