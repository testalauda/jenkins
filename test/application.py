# coding=utf-8
from time import time, sleep
import requests
import json
import settings
import logging
from utils import get_events, apicall_application, retry, get_registry_info, get_region_id,\
    get_node_ip, exec_feature, access_service,create_alb,delete_alb
from env import create_envs, delete_envs
from common import verify_volumes, get_metrics, get_logs, get_logfile
from brewmaster.run import case
from CLaaS.configurations import create_configuration, delete_configuration
from CLaaS.volumes import create_volume, delete_volume, get_volume_id_from_list

logger = logging.getLogger()

headers = {
    "Authorization": "Token " + settings.API_TOKEN,
    'content-type': 'application/json'
}


@retry(times=settings.RETRY_TIMES)
def create_application(name, files_data, region):
    delete_application(name, region)
    time1 = time()
    files = {'services': ('compose.yml', unicode(files_data))}
    (code, text) = apicall_application('create_app', name, region_name=region,
                                       files=files)
    print ("application apicall returns (%d, %s)" % (code, text))
    if code < 200 or code > 300:
        msg = "Error in call create application API {}:{}".format(code, text)
        return {"success": False, "total": msg}
    sleep(5)
    if not get_events(name, "create"):
        return {"success": False, "total": "this action do not have events"}
    app_url = "{}applications/{}/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, name)
    isdeploy = True
    cnt = 0
    while cnt < 240 and isdeploy:
        cnt = cnt + 1
        print('get app status:{}'.format(app_url))
        r = requests.get(app_url, headers=headers)
        if r.status_code > 300 or r.status_code < 200:
            msg = "Get application status_code error: {}, error text:{}".format(r.status_code, r.text)
            return {"success": False, "total": msg}
        if json.loads(r.text)['current_status'] != "Running":
            sleep(3)
            continue
        isdeploy = False
    if isdeploy:
        msg = "Timeout in creating"
        return {"success": False, "total": msg}
    return {"success": True, "total": time()-time1}


def get_applications_detail(app_name):
    logger.info("======== Start get application==========")
    time1 = time()
    get_app_url = "{}applications/{}/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, app_name)
    r = requests.get(get_app_url, headers=headers)
    time2 = time()
    return {
        "status": r.status_code,
        "text": r.text,
        "total": time2 - time1
    }


@retry(times=settings.RETRY_TIMES)
def start_application(name, region):
    logger.info(name + " start application")
    time1 = time()
    (code, text) = apicall_application('start_app', name, region_name=region)
    logger.info(name + " apicall returns (%d, %s)" % (code, text))
    print code, text
    if code < 200 or code >= 300:
        msg = "Error in call start application API {}:{}".format(code, text)
        return {"success": False, "total": msg}
    sleep(5)
    if not get_events(name, "start"):
        return {"success": False, "total": "this action do not have events"}

    app_url = "{}applications/{}/{}".format(settings.API_URL,
                                            settings.CLAAS_NAMESPACE, name)
    isdeploy = True
    cnt = 0
    while cnt < 120 and isdeploy:
        cnt = cnt + 1
        r = requests.get(app_url, headers=headers)
        print json.loads(r.text)['current_status']
        if r.status_code > 300 or r.status_code < 200:
            msg = "Get application status_code error: {},error text:{}".format(r.status_code, r.text)
            return {"success": False, "total": msg}
        if json.loads(r.text)['current_status'] == "PartialRunning":
            return {"success": False, "total": "application is PartialRunning"}
        if json.loads(r.text)['current_status'] != "Running":
            sleep(3)
            continue
        isdeploy = False
    time2 = time()
    if isdeploy:
        msg = "timeout in create application"
        return {"success": False, "total": msg}

    return {"success": True, "total": time() - time1}

def update_application(app_name, files_data, region):
    time1 = time()
    files = {'services': ('compose.yml', unicode(files_data))}
    (code, text) = apicall_application('update_app', app_name, region_name=region,
                                       files=files)
    print ("application apicall returns (%d, %s)" % (code, text))
    if code < 200 or code > 300:
        msg = "Error in call update application API {}:{}".format(code, text)
        return {"success": False, "total": msg}
    sleep(5)
    if not get_events(app_name, "update"):
        return {"success": False, "total": "this action do not have events"}
    app_url = "{}applications/{}/{}".format(settings.API_URL, settings.CLAAS_NAMESPACE, app_name)
    isdeploy = True
    cnt = 0
    while cnt < 240 and isdeploy:
        cnt = cnt + 1
        print('get app status:{}'.format(app_url))
        r = requests.get(app_url, headers=headers)
        print('get app status:r{}'.format(r))
        if r.status_code > 300 or r.status_code < 200:
            msg = "Get application status_code error: {}, error text:{}".format(r.status_code, r.text)
            return {"success": False, "total": msg}
        if json.loads(r.text)['current_status'] != "Running":
            sleep(3)
            continue
        isdeploy = False
    if isdeploy:
        msg = "Timeout in updating"
        return {"success": False, "total": msg}
    return {"success": True, "total": time() - time1}


@retry(times=settings.RETRY_TIMES)
def stop_application(name, region):
    logger.info(name + " stop application")
    time1 = time()
    (code, text) = apicall_application('stop_app', name, region_name=region)
    logger.info(name + " apicall returns (%d, %s)" % (code, text))
    if code < 200 or code >= 300:
        msg = "Error in call stop application API {}:{}".format(code, text)
        return {"success": False, "total": msg}
    sleep(5)
    if not get_events(name, "stop"):
        return {"success": False, "total": "this action do not have events"}

    app_url = "{}applications/{}/{}".format(settings.API_URL,
                                            settings.CLAAS_NAMESPACE, name)
    isdeploy = True
    cnt = 0
    while cnt < 120 and isdeploy:
        cnt = cnt + 1
        r = requests.get(app_url, headers=headers)
        print json.loads(r.text)['current_status']
        if r.status_code > 300 or r.status_code < 200:
            msg = "Get application status_code error: {},error text:{}".format(r.status_code, r.text)
            return {"success": False, "total": msg}
        if json.loads(r.text)['current_status'] != "Stopped":
            sleep(3)
            continue
        isdeploy = False
    time2 = time()
    if isdeploy:
        msg = "Timeout in stopping"
        return {"success": False, "total": msg}
    obj = {
        "success": True,
        "total": time2 - time1
    }
    return obj


@retry(times=settings.RETRY_TIMES)
def delete_application(name, region):
    logger.info(region + " Start delete {}".format(name))

    time1 = time()
    (code, text) = apicall_application("delete_app", name, region_name=region)
    if code < 200 or code >= 300:
        msg = "Error in calling delete API {}:{}".format(code, text)
        return {"success": False, "total": msg}
    sleep(5)
    if not get_events(name, "destroy"):
        return {"success": False, "total": "this action do not have events"}
    print code, text
    app_url = "{}applications/{}/{}".format(settings.API_URL,
                                            settings.CLAAS_NAMESPACE, name)
    cnt = 0
    delete_status = False
    while cnt < 120 and not delete_status:
        cnt = cnt + 1
        r = requests.get(app_url, headers=headers)
        print r.status_code
        if r.status_code <= 300 and r.status_code >= 200:
            sleep(3)
            continue
        delete_status = True
    if not delete_status:
        return {"success": False, "total": "delete application failed"}
    time2 = time()
    sleep(10)

    obj = {"success": True, "total": time2 - time1}
    return obj


def get_yaml(app_name):
    logger.info(" Start get application yaml file content (alauda-compose) {}".format(app_name))
    time1 = time()
    get_app_url = "{}applications/{}/{}/yaml".format(settings.API_URL, settings.CLAAS_NAMESPACE, app_name)
    print('get_yaml:{}'.format(get_app_url))
    r = requests.get(get_app_url, headers=headers)

    time2 = time()
    return {"status": r.status_code, "text": r.text, "total": time2 - time1}


def get_compose_yaml(app_name):
    logger.info(" Start get application compose-yaml file content {}".format(app_name))
    time1 = time()
    get_app_url = "{}applications/{}/{}/compose-yaml".format(settings.API_URL, settings.CLAAS_NAMESPACE, app_name)
    print('get_compose_yaml:{}'.format(get_app_url))
    r = requests.get(get_app_url, headers=headers)

    time2 = time()
    return {"status": r.status_code, "text": r.text, "total": time2 - time1}


def check_service(service_name, app_name):
    logger.info(" Start get application[service{}] envvars content {}".format(service_name, app_name))
    time1 = time()
    get_app_url = "{}services/{}/{}?application={}".format(settings.API_URL, settings.CLAAS_NAMESPACE, service_name,
                                                           app_name)
    print('get_service:{}'.format(get_app_url))
    r = requests.get(get_app_url, headers=headers)

    if r.status_code != 200:
        return {"success": False, "total": "get_service:{} failed".format(service_name)}

    envvar = json.loads(r.text)['instance_envvars']['env1']
    print('envvar:{}'.format(envvar))
    if envvar != 'env-value1':
        return {
            "success": False,
            "total": "service[{}] env1 should be env-value1, but its value is {} "
                .format(envvar)
        }
    app_volume_dir = json.loads(r.text)['volumes'][0]['app_volume_dir']
    print('app_volume_dir:{}'.format(app_volume_dir))
    if app_volume_dir != '/var/lib/mysql':
        return {
            "success": False,
            "total": "service[{}] should have app volume dir /var/lib/mysql, but it is {} "
                .format(app_volume_dir)
        }
    volume_name = json.loads(r.text)['volumes'][0]['volume_name']
    print('volume_name:{}'.format(volume_name))
    if volume_name != '/home/ubuntu':
        return {
            "success": False,
            "total": "service[{}] should have app volume name /home/ubuntu, but it is {} "
                .format(volume_name)
        }

    time2 = time()
    return {"success": True, "total": time2 - time1}


class ApplicationTest(object):
    def application_set_up(self):
        self.app_ha_name = "e2e-app-testha{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.app_raw_name = "e2e-app-testraw{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.app_elb_name = "e2e-app-testelb{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.app_alb_name = "e2e-app-testalb{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.envfile_name = "e2e_app_test_envfile{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        #k8s falnnel模式使用的变量
        self.app_k8s_name = "e2e-app-testk8sflannel{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.k8s_app_config = "e2e-app-config{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.k8s_app_config_key = "e2e-app-config-key{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.k8s_ip_tag = get_node_ip().get("node_tag", None).split(":")[1]
        self.app_flannel_service_name = 'e2e-app-flannel-service{}'.format(settings.SERVICE_CLAAS_REGION[0]).replace(
            "_", "-")
        # k8s host 模式的应用使用的变量
        self.app_k8s_host_name = "e2e-app-testk8shost{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.app_host_service_name = 'e2e-app-host-service{}'.format(settings.SERVICE_CLAAS_REGION[0]).replace(
            "_", "-")
        self.app_k8s_env_file = "e2e-app-k8s-envfile{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.app_k8s_gfs_volume = "e2e-app-k8s-gfsvolume{}".format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        # k8s 支持elb和ebs的应用使用的变量
        self.app_k8s_exlb_service = 'e2e-app-k8s-exlb{}'.format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.app_k8s_innerlb_service = 'e2e-app-k8s-innerlb{}'.format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.app_k8s_elb_name = 'e2e-app-elb{}'.format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")
        self.app_k8s_ebs_name = 'e2e-ebs-volume{}'.format(settings.SERVICE_CLAAS_REGION[0]).replace("_", "-")


        self.app_region = settings.SERVICE_CLAAS_REGION[0]
        print('self.app_region:{}'.format(self.app_region))
        self.namespace = settings.CLAAS_NAMESPACE
        print('settings.SERVICE_CLAAS_REGION:{}'.format(settings.SERVICE_CLAAS_REGION))
        # get alb region
        self.haproxy = get_region_id(self.app_region).get("haproxy_ip", None)
        if self.haproxy:
            self.haproxy = "haproxy-" + self.haproxy.replace('.', '-')
        print('self.alb_region:{}'.format(self.app_region))
        print('self.haproxy:{}'.format(self.haproxy))

        #     create an env-file

        create_envs(self.envfile_name)

    def application_tear_down(self):
        delete_application(self.app_ha_name, self.app_region)
        delete_application(self.app_elb_name, self.app_region)
        delete_application(self.app_raw_name, self.app_region)
        delete_application(self.app_alb_name, self.app_region)
        delete_application(self.app_k8s_name, self.app_region)
        delete_application(self.app_k8s_host_name, self.app_region)
        delete_application(self.app_k8s_elb_name, self.app_region)
        delete_alb(self.app_k8s_exlb_service)
        delete_alb(self.app_k8s_innerlb_service)
        delete_envs(self.envfile_name)
        delete_configuration(self.k8s_app_config)
        if 'glusterfs' in ((self.region_data)['data']['features']['volume']['features']):
            if get_volume_id_from_list(self.app_k8s_gfs_volume)["success"] != False:
                delete_volume(get_volume_id_from_list(self.app_k8s_gfs_volume)["volume_id"],
                              self.app_k8s_gfs_volume)
        if 'ebs' in ((self.region_data)['data']['features']['volume']['features']):
            if get_volume_id_from_list(self.app_k8s_ebs_name)["success"] != False:
                delete_volume(get_volume_id_from_list(self.app_k8s_ebs_name)["volume_id"], self.app_k8s_ebs_name)
        delete_envs(self.app_k8s_env_file)


    @case
    def create_application__applications(self):
        ''' create app with most alauda yaml features: command|entrypoint|environment|domain|links|net|number|size|
        volumes|ports|expose|alauda_lb|internal_ports'''

        print('self.internal_data:{}'.format(self.internal_data))
        self.create_app_action(self.app_ha_name, self.internal_data, self.app_region, 'HA', None, False)

        yaml_content = None
        if settings.ENV == 'private':
            yaml_content = "helloworld:\n image: {}/{}:{}\n size: XXS\n ports:\n - '80/http'\n" \
                .format(get_registry_info().get('registry_url', None), settings.PRIVATE_REPO, settings.IMAGE_TAG)
        else:
            yaml_content = "redis:\n alauda_lb:\n  internal_ports:\n  - '6379'\n  lb_type: HA\n" \
                                 " image: {}/library/redis:latest\n size: XXS\n net: bridge\n number: 1\n" \
                                 "web:\n alauda_lb: HA\n command: python app.py\n image: {}/alauda/flask-redis:latest" \
                                 "\n size: XS\n links:\n - redis:redis\n ports:\n - '80/http'" \
                                 "\ntest-volume:\n entrypoint: /start.sh\n image: index.alauda.cn/alauda/volume-test:latest\n " \
                                 "environment:\n - env1=env-value1\n volumes:\n - /home/ubuntu:/var/lib/mysql" \
                                 "\n env_file:\n - {}\n size: CUSTOMIZED\n cpu_quota: 0.125\n mem_limit: 100" \
                .format(settings.REGISTRY_URL, settings.REGISTRY_URL, self.envfile_name)

        print('yaml_content:{}'.format(yaml_content))
        self.create_app_action(self.app_ha_name, yaml_content, self.app_region, 'HA', None, True)

    @case
    def create_elb_application__applications(self):
        ''' create app with most alauda yaml features: command|entrypoint|environment|domain|links|net|number|size|
        volumes|ports|expose|alauda_lb|internal_ports'''

        yaml_content = None
        if settings.ENV == 'private':
            yaml_content = "helloworld:\n image: {}/{}:{}\n size: XXS\n ports:\n - '80/http'\n" \
                .format(get_registry_info().get('registry_url', None), settings.PRIVATE_REPO, settings.IMAGE_TAG)
        else:
            yaml_content = "redis:\n alauda_lb:\n  internal_ports:\n  - '6379'\n  lb_type: ELB\n" \
                                 " image: {}/library/redis:latest\n size: XXS\n net: bridge\n number: 1\n" \
                                 "web:\n alauda_lb: ELB\n command: python app.py\n image: {}/alauda/flask-redis:latest" \
                                 "\n size: XS\n links:\n - redis:redis\n ports:\n - '80:80/http'" \
                                 "\ntest-volume:\n entrypoint: /start.sh\n image: index.alauda.cn/alauda/volume-test:latest\n " \
                                 "environment:\n - env1=env-value1\n volumes:\n - /home/ubuntu:/var/lib/mysql" \
                                 "\n env_file:\n - {}\n size: CUSTOMIZED\n cpu_quota: 0.125\n mem_limit: 100" \
                .format(settings.REGISTRY_URL, settings.REGISTRY_URL, self.envfile_name)

        print('yaml_content:{}'.format(yaml_content))
        self.create_app_action(self.app_elb_name, yaml_content, self.app_region, 'ELB', None, True)

    @case
    def create_alb_application__alb_applications(self):
        ''' create app with most alauda yaml features: command|entrypoint|environment|domain|links|net|number|size|
        volumes|ports|expose|alauda_lb|internal_ports'''
        if self.app_region is not None:
            yaml_content = None
            if settings.ENV == 'private':
                yaml_content = "helloworld:\n alauda_lb: ALB\n net: flannel\n image: {}/{}:{}\n size: XXS\n ports:\n - '{}:80:80/http'\n" \
                    .format(get_registry_info().get('registry_url', None), settings.PRIVATE_REPO, settings.IMAGE_TAG, self.haproxy)
            else:
                yaml_content = "redis:\n alauda_lb: ALB\n ports:\n - '{}:6379:6379'\n" \
                                     " image: {}/library/redis:latest\n size: XXS\n net: bridge\n number: 1\n" \
                                     "web:\n alauda_lb: ALB\n command: python app.py\n image: {}/alauda/flask-redis:latest" \
                                     "\n size: XS\n links:\n - redis:redis\n ports:\n - '{}:18080:80/http'" \
                                     "\ntest-volume:\n entrypoint: /start.sh\n image: index.alauda.cn/alauda/volume-test:latest\n " \
                                     "environment:\n - env1=env-value1\n volumes:\n - /home/ubuntu:/var/lib/mysql" \
                                     "\n env_file:\n - {}\n size: CUSTOMIZED\n cpu_quota: 0.125\n mem_limit: 100" \
                    .format(self.haproxy, settings.REGISTRY_URL, settings.REGISTRY_URL, self.haproxy, self.envfile_name)

            print('yaml_content:{}'.format(yaml_content))
            self.create_app_action(self.app_alb_name, yaml_content, self.app_region, 'ALB', self.haproxy, True)
        else:
            return {"success": True, "total": "there is no alb region, skip the case"}

    @case
    def create_k8s_flannel_app__k8s_applications(self):
        ''' create app with most alauda yaml features: environment|links|net|number|size|
        volumes|alauda_lb|amount_points|labels'''
        if self.app_region is not None:
            test_flag = True
            ret1 = create_configuration(self.k8s_app_config, "value", self.k8s_app_config_key)
            self.assert_successful(ret1)

            if settings.ENV == 'private':
                yaml_content = "{}:\n alauda_lb: ALB\n net: flannel\n image: {}/{}:{}\n number: 1\n" \
                               "size: XXS\n ports:\n - '{}:80:80/http'\n" \
                               " environment:\n - k8s_key=k8s-value\n - __ALAUDA_FILE_LOG_PATH__=/home/*.txt\n" \
                               " volumes:\n - /home/:/var/\n mount_points:\n - path: /home/abc\n   config: {}/{}\n" \
                               " labels:\n - 'constraint:node==ip:{}'" \
                    .format(self.app_flannel_service_name, get_registry_info().get('registry_url', None),
                            settings.PRIVATE_REPO, settings.IMAGE_TAG, self.haproxy,
                            self.k8s_app_config, self.k8s_app_config_key, self.k8s_ip_tag
                            )
            else:
                # APP yaml支持flannel模式服务，添加环境变量，添加配置文件，添加local的volume，指定日志文件，部署在指定的机器上
                yaml_content = "{}:\n alauda_lb: ALB\n ports:\n - '{}:80:80/http'\n" \
                               " image: {}/{}/hello-world:latest\n size: XXS\n net: flannel\n number: 1\n" \
                               " environment:\n - k8s_key=k8s-value\n - __ALAUDA_FILE_LOG_PATH__=/home/*.txt\n"\
                               " volumes:\n - /home/:/var/\n mount_points:\n - path: /home/abc\n   config: {}/{}\n"\
                               " labels:\n - 'constraint:node==ip:{}'"\
                    .format(self.app_flannel_service_name, self.haproxy, settings.REGISTRY_URL,
                            settings.CLAAS_NAMESPACE, self.k8s_app_config, self.k8s_app_config_key, self.k8s_ip_tag)

            print('yaml_content:{}'.format(yaml_content))
            # self.create_app_action(self.app_k8s_name, yaml_content, self.app_region, 'ALB', self.haproxy, False)
            #创建应用 会判断应用的最终状态，如果不是Running 直接返回
            ret1 = create_application(self.app_k8s_name, files_data=yaml_content, region=self.app_region)
            self.assert_successful(ret1)

            # 验证应用内的服务是否可以访问，失败不影响后续操作
            ret_access_service = access_service(self.app_flannel_service_name, self.haproxy, self.app_k8s_name)
            if not ret_access_service['success']:
                test_flag = False

            # 检查应用创建成功后yaml,失败后返回，因为会影响更新
            ret2 = get_yaml(self.app_k8s_name)
            if ret2['status'] != 200:
                test_flag = False
                ret2 = {
                    "success": False,
                    "message": "get application yaml failed, jakiro api error code {}, error:{}".format(ret2["status"],
                                                                                                          ret2["text"])
                }
            elif self.app_flannel_service_name not in ret2['text']:
                test_flag = False
                ret2 = {
                    "success": False,
                    "message": "service_name is {},not in yaml:{}".format(self.app_flannel_service_name, ret2['text'])
                }
            else:
                update_yaml =  ret2['text'].replace("XXS", "XS")
                ret2 = {
                    "success": True,
                    "total": ret2["total"]
                }
            self.assert_successful(ret2)
            # 检查应用的compose-yaml 失败后不影响后续操作
            ret3 = get_compose_yaml(self.app_k8s_name)
            if ret3['status'] != 200:
                test_flag = False
                ret3 = {
                    "success": False,
                    "message": "get application compose yaml failed, jakiro api error code {},error:{}".format(
                        ret3['status'], ret3['text'])
                }
            elif self.app_flannel_service_name not in ret3['text']:
                test_flag = False
                ret3 = {
                    "success": False,
                    "message": "service_name is {},not in yaml:{}".format(self.app_flannel_service_name, ret3['text'])
                }
            else:
                ret3 = {
                    "success": True,
                    "total": ret3["total"]
                }

            # 验证环境变量是否添加进去 失败可以继续后面测试
            ret4 = exec_feature(self.app_flannel_service_name, self.namespace, command="env",
                                commands_string="k8s_key=k8s-value", app_name=self.app_k8s_name)
            if not ret4['success']:
                test_flag = False
            # 验证配置文件是否添加进去 失败可以继续后面测试
            ret5 = exec_feature(self.app_flannel_service_name, self.namespace,
                                command="'cat /home/abc'", commands_string="value", app_name=self.app_k8s_name)
            if not ret5['success']:
                test_flag = False

            # 判断存储卷类型 不阻塞后面的测试
            ret6 = verify_volumes(self.app_flannel_service_name, "host_path", self.app_k8s_name)
            if not ret6['success']:
                test_flag = False

            # 判断是否有Metrics 不阻塞后面的测试
            ret7 = get_metrics(self.app_flannel_service_name, self.app_k8s_name)
            if not ret7['success']:
                test_flag = False

            ret_stop = stop_application(self.app_k8s_name, self.app_region)
            self.assert_successful(ret_stop)

            ret_start = start_application(self.app_k8s_name, self.app_region)
            self.assert_successful(ret_start)
            #验证更新操作，失败直接返回
            ret_update = update_application(self.app_k8s_name, files_data=update_yaml, region=self.app_region)
            self.assert_successful(ret_update)

            # check 服务的日志
            ret14 = get_logs(self.app_flannel_service_name, app_name=self.app_k8s_name)
            if not ret14['success']:
                test_flag = False
            # check 日志文件
            ret15 = get_logfile(self.app_flannel_service_name, self.app_k8s_name)
            if not ret15['success']:
                test_flag = False
            #删除应用
            ret_delete = delete_application(self.app_k8s_name, self.app_region)
            self.assert_successful(ret_delete)
            result = {
                'success': test_flag,
                "create application": ret1,
                "access sercie ": ret_access_service,
                "get yaml": ret2,
                "get compose yaml": ret3,
                "get service env": ret4,
                "get service config": ret5,
                "get service volume type": ret6,
                "get service metrics": ret7,
                "stop application": ret_stop,
                "start application": ret_start,
                "update application": ret_update,
                "get service log": ret14,
                "get service logfile": ret15,
                "delete service": ret_delete
            }
            self.assert_successful(result)
            return {"success": True, "total": "All success"}

        else:
            return {"success": True, "total": "there is no alb region, skip the case"}

    @case
    def create_k8s_host_app__k8s_applications(self):
        if self.app_region is not None and 'glusterfs' in (
        (self.region_data)['data']['features']['volume']['features']):
            test_flag = True
            ret_env = create_envs(self.app_k8s_env_file)
            self.assert_successful(ret_env)

            ret_volume = create_volume(self.app_k8s_gfs_volume, 'glusterfs', None)
            self.assert_successful(ret_volume)
            volume_id = ret_volume['volume_id']

            if settings.ENV == 'private':
                yaml_content = "{}:\n alauda_lb: ALB\n net: host\n image: {}/{}:{}\n" \
                               "size: XXS\n ports:\n - '{}:80:80/http'\n number :1\n"\
                               "env_file: {}\n volumes\n - {}:/var/\n" \
                    .format(self.app_host_service_name, get_registry_info().get('registry_url', None),
                            settings.PRIVATE_REPO, settings.IMAGE_TAG,
                            self.haproxy, self.app_k8s_env_file, self.app_k8s_gfs_volume)
            else:
                # APP yaml支持host模式服务，添加环境变量文件，添加gfs的volume
                yaml_content = "{}:\n alauda_lb: ALB\n ports:\n - '{}:81:81/http'\n" \
                               " image: {}/{}/hello-world:latest\n size: XXS\n net: host\n number: 1\n" \
                               " env_file: {}\n volumes:\n - {}:/var/\n" \
                    .format(self.app_host_service_name, self.haproxy, settings.REGISTRY_URL,
                            settings.CLAAS_NAMESPACE, self.app_k8s_env_file, self.app_k8s_gfs_volume)

            print('yaml_content:{}'.format(yaml_content))
            # self.create_app_action(self.app_k8s_name, yaml_content, self.app_region, 'ALB', self.haproxy, False)
            # 创建应用 会判断应用的最终状态，如果不是Running 直接返回
            ret1 = create_application(self.app_k8s_host_name, files_data=yaml_content, region=self.app_region)
            self.assert_successful(ret1)


            # 验证环境变量文件是否添加进去 失败可以继续后面测试
            ret4 = exec_feature(self.app_host_service_name, self.namespace, command="env",
                                commands_string="key=value", app_name=self.app_k8s_host_name)
            if not ret4['success']:
                test_flag = False

            # 判断存储卷类型 不阻塞后面的测试
            ret6 = verify_volumes(self.app_host_service_name, volume_id, self.app_k8s_host_name)
            if not ret6['success']:
                test_flag = False

            # 判断是否有Metrics 不阻塞后面的测试
            ret7 = get_metrics(self.app_host_service_name, self.app_k8s_host_name)
            if not ret7['success']:
                test_flag = False

            # check 服务的日志
            ret14 = get_logs(self.app_host_service_name, app_name=self.app_k8s_host_name)
            if not ret14['success']:
                test_flag = False
            # 删除应用
            ret_delete = delete_application(self.app_k8s_host_name, self.app_region)
            self.assert_successful(ret_delete)
            result = {
                'success': test_flag,
                "create envfile": ret_env,
                "create gfs volume": ret_volume,
                "create application": ret1,
                "get service env": ret4,
                "get service volume type": ret6,
                "get service metrics": ret7,
                "get service log": ret14,
                "delete service": ret_delete
            }
            self.assert_successful(result)
            return {"success": True, "total": "All success"}

        else:
            return {"success": True, "total": "there is no alb region, skip the case"}

    @case
    def create_k8s_link_app__k8s_applications(self):
        if self.app_region is not None and 'ebs' in (
                (self.region_data)['data']['features']['volume']['features']):
            test_flag = True
            # 创建需要的内网ELB 失败返回
            ret_innerlb = create_alb(self.app_k8s_innerlb_service, create_type='manual', type='elb',
                                   alb_region=settings.SERVICE_CLAAS_REGION[0], address_type="internal")
            self.assert_successful(ret_innerlb)
            # 创建需要的外网ELB 失败返回
            ret_exlb = create_alb(self.app_k8s_exlb_service, create_type='manual', type='elb',
                                  alb_region=settings.SERVICE_CLAAS_REGION[0])
            self.assert_successful(ret_exlb)
            # 创建需要的ebs volume 失败返回
            ret_volume = create_volume(self.app_k8s_ebs_name, 'ebs', 'gp2')
            self.assert_successful(ret_volume)
            volume_id = ret_volume['volume_id']

            # APP yaml支持外网ELBflannel服务挂在ebs的存储卷 并且link 内网ELB host模式服务(支持ebs的不可能是纯私有，所以不加判断)
            yaml_content = "{}:\n alauda_lb: ALB\n ports:\n - '{}:80:80/http'\n" \
                           " image: {}/{}/hello-world:latest\n size: XXS\n net: flannel\n number: 1\n" \
                           " volumes:\n - {}:/var/\n{}:\n alauda_lb: ALB\n ports:\n - '{}:82:82/http'\n" \
                           " image: {}/{}/hello-world:latest\n size: XXS\n net: host\n number: 1\n links:\n - {}:{}\n" \
                .format(self.app_k8s_exlb_service, self.app_k8s_exlb_service, settings.REGISTRY_URL,
                        settings.CLAAS_NAMESPACE, self.app_k8s_ebs_name, self.app_k8s_innerlb_service,
                        self.app_k8s_innerlb_service, settings.REGISTRY_URL, settings.CLAAS_NAMESPACE,
                        self.app_k8s_exlb_service, self.app_k8s_exlb_service)

            print('yaml_content:{}'.format(yaml_content))
            # 创建应用 会判断应用的最终状态，如果不是Running 直接返回
            ret1 = create_application(self.app_k8s_elb_name, files_data=yaml_content, region=self.app_region)
            self.assert_successful(ret1)

            # 判断存储卷类型 不阻塞后面的测试
            ret6 = verify_volumes(self.app_k8s_exlb_service, volume_id, self.app_k8s_elb_name)
            if not ret6['success']:
                test_flag = False

            ret_link = get_applications_detail(self.app_k8s_elb_name)
            app_content = json.loads(ret_link['text'])
            if ret_link["status"] != 200:
                test_flag = False
                ret_link = {
                    "success": False,
                    "message": "failed in get app detail, jakiro api error code {}, error:{}".format(ret_link["status"],
                                                                                                     ret_link["text"])
                }
            elif app_content['services'][0]['service_name'] == self.app_k8s_innerlb_service:
                if app_content['services'][0]['linked_to_apps'][self.app_k8s_exlb_service] != self.app_k8s_exlb_service:
                    test_flag = False
                    ret_link = {
                        "success": False,
                        "message": "failed in get app detail, link service is [{}], but inpect:{} ".
                            format(app_content['services'][0]['linked_to_apps'], self.app_k8s_exlb_service)
                    }
            elif app_content['services'][1]['service_name'] == self.app_k8s_innerlb_service:
                if app_content['services'][1]['linked_to_apps'][self.app_k8s_exlb_service] != self.app_k8s_exlb_service:
                    test_flag = False
                    ret_link = {
                        "success": False,
                        "message": "failed in get app detail, link service is [{}], but inpect:{} ".
                            format(app_content['services'][1]['linked_to_apps'], self.app_k8s_exlb_service)
                    }
            else:
                ret_link = {"success": True, "total": ret_link["total"]}
            #删除ELB
            ret7 = delete_alb(self.app_k8s_innerlb_service)
            self.assert_successful(ret7)
            ret8 = delete_alb(self.app_k8s_exlb_service)
            self.assert_successful(ret8)
            # 删除应用
            ret_delete = delete_application(self.app_k8s_elb_name, self.app_region)
            self.assert_successful(ret_delete)
            result = {
                'success': test_flag,
                "create gfs volume": ret_volume,
                "create application": ret1,
                "get service volume type": ret6,
                "get app link": ret_link,
                "delete service": ret_delete
            }
            self.assert_successful(result)
            return {"success": True, "total": "All success"}

        else:
            return {"success": True, "total": "there is no alb region, skip the case"}

    @case
    def create_raw_application__applications(self):
        ''' create app with most alauda yaml features: command|entrypoint|environment|domain|links|net|number|size|
        volumes|ports|expose|alauda_lb|internal_ports'''

        yaml_content = None
        if settings.ENV == 'private':
            yaml_content = "helloworld:\n alauda_lb: RAW\n net: flannel\n image: {}/{}:{}\n size: XXS\n ports:\n - '80'\n" \
                .format(get_registry_info().get('registry_url', None), settings.PRIVATE_REPO, settings.IMAGE_TAG, self.haproxy)
        else:
            yaml_content = "redis:\n alauda_lb: RAW\n ports:\n - '6379'\n" \
                                 " image: {}/library/redis:latest\n size: XXS\n net: bridge\n number: 1\n" \
                                 "web:\n alauda_lb: RAW\n command: python app.py\n image: {}/alauda/flask-redis:latest" \
                                 "\n size: XS\n links:\n - redis:redis\n ports:\n - '80/http'" \
                                 "\ntest-volume:\n entrypoint: /start.sh\n image: index.alauda.cn/alauda/volume-test:latest\n " \
                                 "environment:\n - env1=env-value1\n volumes:\n - /home/ubuntu:/var/lib/mysql" \
                                 "\n env_file:\n - {}\n size: CUSTOMIZED\n cpu_quota: 0.125\n mem_limit: 100" \
                .format(settings.REGISTRY_URL, settings.REGISTRY_URL, self.envfile_name)

        print('yaml_content:{}'.format(yaml_content))
        self.create_app_action(self.app_raw_name, yaml_content, self.app_region, 'RAW', None, True)

    def create_app_action(self, app_name, yaml, region, lb_type='HA', lb_name=None, checkservice=False):
        ret = create_application(app_name, files_data=yaml, region=region, lb_type=lb_type, lb_name=lb_name)
        self.assert_successful(ret)

        ret = get_yaml(app_name)
        self.assert_successful(ret)

        ret = get_compose_yaml(app_name)
        self.assert_successful(ret)

        if checkservice:
            ret = check_service('test-volume', app_name)
            self.assert_successful(ret)

        ret = stop_application(app_name, region)
        self.assert_successful(ret)

        ret = start_application(app_name, region)
        self.assert_successful(ret)

        ret = delete_application(app_name, region)
        self.assert_successful(ret)
