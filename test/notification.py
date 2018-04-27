from time import time
from utils import get_events, retry
import logging
import settings
import requests
import json
from brewmaster.run import case
from uuid import uuid4

logger = logging.getLogger()
REGIONS = settings.SERVICE_CLAAS_REGION
uuid = ''
headers = {
    "Authorization": "Token " + settings.API_TOKEN,
    'content-type': 'application/json'
}
url = settings.API_URL


@retry(times=settings.RETRY_TIMES)
def create_notification(name, notificationtype, notificationvalue):
    delete_notification(name)
    time1 = time()
    post_url = url + 'notifications/' + settings.CLAAS_NAMESPACE
    payload = {
        "namespace": settings.CLAAS_NAMESPACE,
        "name": name,
        "subscriptions": [{
            "remark": "",
            "recipient": notificationvalue,
            "method": notificationtype
        }]
    }
    print "POST URL - {}".format(post_url)
    print "PAYLOAD - \n{}".format(payload)
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    print "Response Code - {}".format(r.status_code)
    print "Response body - \n{}".format(r.text)
    if r.status_code != 201:
        return {"success": False, "total": "create notification error in call jakiro api:{}:,error code:{} ".format(r.text, r.status_code)}
    if not get_events(name, "create"):
        return {"success": False, "total": "this action do not have events"}
    if 'uuid' in json.loads(r.text):
        global uuid
        uuid = json.loads(r.text)['uuid']
    else:
        return {"success": False, "total": "uuid not return after create notification"}
    time2 = time()
    return {
        "success": True,
        "total": time2 - time1,
        "uuid" :uuid
    }


@retry(times=settings.RETRY_TIMES)
def update_notification(name, notificationtype, notificationvalue):
    time1 = time()
    put_url = '{}notifications/{}/{}'.format(url, settings.CLAAS_NAMESPACE, name)
    payload = {
        "namespace": settings.CLAAS_NAMESPACE,
        "name": name,
        "subscriptions": [{
            "remark": "",
            "recipient": notificationvalue,
            "method": notificationtype
        }]
    }
    print "PUT URL - {}".format(put_url)
    print "PAYLOAD - \n{}".format(payload)
    r = requests.put(put_url, data=json.dumps(payload), headers=headers)
    print "Response - {}".format(r)
    if r.status_code != 200:
        return {"success": False, "total": "update notification error in call jakiro api: {}, error code:".format(r.text, r.text)}
    if not get_events(name, "update"):
        return {"success": False, "total": "this action do not have events"}
    time2 = time()
    return {
        "success": True,
        "total": time2 - time1
        }


@retry(times=settings.RETRY_TIMES)
def get_notification(name, notificationtype, notificationvalue):
    time1 = time()
    get_url = '{}notifications/{}/{}'.format(url, settings.CLAAS_NAMESPACE, name)
    print "GET URL - {}".format(get_url)
    r = requests.get(get_url, headers=headers)
    print "Response Code - {}".format(r.status_code)
    print "Response body - \n{}".format(r.text)
    if r.status_code != 200:
        return {"success": False, "total": "get notification error text:{}, error code:{}".format(r.text, r.status_code)}
    if "subscriptions" in json.loads(r.text):
        recipient = json.loads(r.text)['subscriptions'][0]['recipient']
        type = json.loads(r.text)['subscriptions'][0]['method']
        if recipient == notificationvalue and type == notificationtype:
            time2 = time()
            return {
                "success": True,
                "total": time2 - time1
            }
        else:
            return {"success": False, "total": "{}-{} not in notification".format(notificationtype, notificationvalue)}
    else:
        return {"success": False, "total": "subscriptions not in notification"}


@retry(times=settings.RETRY_TIMES)
def delete_notification(name):
    time1 = time()
    delete_url = '{}notifications/{}/{}'.format(url, settings.CLAAS_NAMESPACE, name)
    print "DELETE URL - {}".format(delete_url)
    r = requests.delete(delete_url, headers=headers)
    print "Response - {}".format(r)
    if r.status_code != 204:
        return {"success": False, "total": "delete notification error text:{}, error code:{}".format(r.text, r.status_code)}
    if not get_events(name, "destroy"):
        return {"success": False, "total": "this action do not have events"}
    r = requests.get(delete_url, headers=headers)
    if 'errors' in json.loads(r.text):
        error_message = json.loads(r.text)['errors'][0]['message']
        if error_message == 'The requested resource does not exist.':
            time2 = time()
            obj = {
                "success": True,
                "total": time2 - time1
            }
            return obj
        else:
            return {"success": False, "total": "error message is incorrect in call jakiro api"}
    else:
        return {"success": False, "total": "delete notification failed"}

class NotificationTest(object):

    def notification_set_up(self):
        self.create_notification_name = "e2e-notification-test{}".format(settings.SERVICE_CLAAS_REGION[0])

    def notification_tear_down(self):
        delete_notification(self.create_notification_name)

    @case
    def create_notification__notifications(self):
        ret1 = create_notification(self.create_notification_name, 'email', 'yuzhou@alauda.io')

        # asserting creation ok
        return self.assert_successful(ret1)

        ret2 = update_notification(self.create_notification_name, 'email', 'hchan@alauda.io')

        self.assert_successful(ret2)

        ret3 = get_notification(self.create_notification_name, 'email', 'hchan@alauda.io')

        self.assert_successful(ret3)

        ret4 = delete_notification(self.create_notification_name)

        self.assert_successful(ret4)
        return {
            'success': True,
            'create notification': ret1,
            'update notification': ret2,
            'get notification': ret3,
            'delete notification': ret4
        }

