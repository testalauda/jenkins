# coding=utf-8
import logging
import settings
import data
import json
import requests
from common import create_service, delete_app, get_metrics, stop_app, start_app, update_service, get_logs,\
    verify_volumes, get_logfile
from time import time, sleep
from utils import get_region_id, access_service, get_haproxy, exec_feature, get_node_ip, apicall_claas_service, \
    create_alb, delete_alb
from brewmaster.run import case
from CLaaS.env import create_envs, delete_envs
from CLaaS.volumes import create_volume, delete_volume, get_volume_id_from_list

logger = logging.getLogger()
REGIONS = settings.SERVICE_CLAAS_REGION
headers = {
    "Authorization": "Token " + settings.API_TOKEN,
    'content-type': 'application/json'
}


def check_node(service_name, nodetag):
    print "===========get service detail to check node============"
    time1 = time()
    (code, service_detail) = apicall_claas_service('get_service', service_name)
    if code != 200:
        return {"success": False,
                "total": "get service failed, error code is {}.error message is ".format(code, service_detail)}
    # 判断容器部署在哪台机器
    print "service detail is {}".format(service_detail)
    instances = json.loads(service_detail)['instances']
    for i in range(0, len(instances)):
        if (instances[i]['host_ip'].replace('.', '-') not in nodetag):
            return {"success": False,
                    "total": "instance in host:{}, nodetag ip:{}".format(instances[i]['host_ip'], nodetag)}
    time2 = time()
    return {"success": True, "total": time2 - time1}


class K8sServiceTest(object):

    def k8s_service_set_up(self):
        self.obj = {}
        self.node_tag = get_node_ip().get("node_tag", None)
        self.k8s_flannel_service = "k8s-flannel-service"
        self.k8s_host_service = "k8s-host-service"
        self.k8s_healthycheck_service = "k8s-healthycheck-service"
        self.k8s_exelb_service = "k8s-exelb-service"
        self.k8s_innerelb_service = "k8s-innerelb-service"
        self.k8s_external_elb = "k8s-external-elb"
        self.k8s_internal_elb = "k8s-internal-elb"
        self.namespace = settings.CLAAS_NAMESPACE
        self.haproxy = get_region_id(settings.SERVICE_CLAAS_REGION[0]).get("haproxy_ip", None)
        self.k8s_envfile = "k8s-env-file"
        self.gluster_name = "k8s-gfs-volume"
        self.ebs_name = "k8s-ebs-volume{}".format(settings.SERVICE_CLAAS_REGION[0])
        if self.haproxy:
            self.haproxy = "haproxy-" + self.haproxy.replace('.', '-')

    def k8s_service_tear_down(self):
        delete_app(self.k8s_flannel_service, settings.SERVICE_CLAAS_REGION[0])
        delete_app(self.k8s_host_service, settings.SERVICE_CLAAS_REGION[0])
        delete_app(self.k8s_healthycheck_service)
        delete_app(self.k8s_exelb_service)
        delete_app(self.k8s_innerelb_service)
        delete_envs(self.k8s_envfile)
        delete_alb(self.k8s_external_elb)
        delete_alb(self.k8s_internal_elb)
        #删除volume
        if 'ebs' in ((self.region_data)['data']['features']['volume']['features']):
            if get_volume_id_from_list(self.ebs_name)["success"] != False:
                delete_volume(get_volume_id_from_list(self.ebs_name)["volume_id"], self.ebs_name)


        if 'glusterfs' in ((self.region_data)['data']['features']['volume']['features']):
            if get_volume_id_from_list(self.gluster_name)["success"] != False:
                delete_volume(get_volume_id_from_list(self.gluster_name)["volume_id"],
                              self.gluster_name)

    @case
    def k8s_flannel__k8s_service(self):
        # 创建flannel服务支持:环境变量，配置文件，local volume，日志文件，部署到指定机器
        if self.haproxy:
            test_flag = True
            ret1 = get_haproxy(self.haproxy)

            self.assert_successful(ret1)

            k8sFlannelData = data.ServiceData(self.k8s_flannel_service, self.namespace, settings.SERVICE_CLAAS_REGION[0],
                                              lb_type='haproxy', alb_name=self.haproxy, lb_id=ret1['haproxy_id'],
                                              node_tag=self.node_tag.split(":")[1], mipn_enabled=True)

            #创建服务支持 环境变量 local volume，配置文件，指定日志文件，部署在指定的机器上  block后面操作
            ret2 = create_service(self.k8s_flannel_service, k8sFlannelData.k8s_flannel_service(), settings.SERVICE_CLAAS_REGION[0])
            self.assert_successful(ret2)
            #验证服务是否可以访问 失败可以继续后面测试
            ret3 = access_service(self.k8s_flannel_service, self.haproxy)
            if not ret3['success']:
                test_flag = False
            #验证环境变量是否添加进去 失败可以继续后面测试
            ret4 = exec_feature(self.k8s_flannel_service, self.namespace, command="env", commands_string="k8s_key=k8s_value")
            if not ret4['success']:
                test_flag = False
            #验证配置文件是否添加进去 失败可以继续后面测试
            ret5 = exec_feature(self.k8s_flannel_service, self.namespace, command="'cat /home/abc'", commands_string="config")
            if not ret5['success']:
                test_flag = False
            #判断存储卷类型 不阻塞后面的测试
            ret6 = verify_volumes(self.k8s_flannel_service, "host_path")
            if not ret6['success']:
                test_flag = False
            #判断是否有Metrics 不阻塞后面的测试
            ret7 = get_metrics(self.k8s_flannel_service)
            if not ret7['success']:
                test_flag = False
            # 停止服务 如果失败block后面操作
            ret8 = stop_app(self.k8s_flannel_service)
            self.assert_successful(ret8)
            #启动服务 如果失败block 后面操作
            ret9= start_app(self.k8s_flannel_service, num=1)
            self.assert_successful(ret9)
            #scale up 服务，更新服务的数量和size，失败block后面操作
            ret10 = update_service(self.k8s_flannel_service, num=2, size="XS")
            self.assert_successful(ret10)
            #check 所有的容器都部署在指定的机器上 不阻塞后面的测试
            ret11 = check_node(self.k8s_flannel_service,self.node_tag)
            if not ret11['success']:
                test_flag = False
            # scale down 服务更新服务的数量和size  失败block后面操作
            ret12 = update_service(self.k8s_flannel_service, num=1, size="XXS")
            self.assert_successful(ret12)
            # check 所有的容器都部署在指定的机器上 不阻塞后面的测试
            ret13 = check_node(self.k8s_flannel_service, self.node_tag)
            if not ret13['success']:
                test_flag = False
            # check 服务的日志
            ret14 = get_logs(self.k8s_flannel_service)
            if not ret14['success']:
                test_flag = False
            #check 日志文件
            ret15 = get_logfile(self.k8s_flannel_service)
            if not ret15['success']:
                test_flag = False
            #删除服务
            ret16 = delete_app(self.k8s_flannel_service, settings.SERVICE_CLAAS_REGION[0])
            if not ret16['success']:
                test_flag = False

            result = {
                'success': test_flag,
                "get haproxy id ": ret1,
                "create k8s haproxy service": ret2,
                "access sercie ": ret3,
                "get service env": ret4,
                "get servie config": ret5,
                "get service volume type": ret6,
                "get service metrics": ret7,
                "stop service": ret8,
                "start service": ret9,
                "scale up service": ret10,
                "check instance in node": ret11,
                "scale down service": ret12,
                "check instance in node": ret13,
                "get service log": ret14,
                "get service logfile": ret15,
                "delete service": ret16
            }
            self.assert_successful(result)
            return result

    @case
    def k8s_host__k8s_service(self):
        if self.haproxy:
            #设置flag
            test_flag = True
            #创建部署服务需要的环境变量文件 创建失败就直接返回
            ret1 = create_envs(self.k8s_envfile)
            self.assert_successful(ret1)
            #创建部署服务需要的glustfs存储卷，创建失败直接返回
            ret2 = create_volume(self.gluster_name, 'glusterfs', None)
            self.assert_successful(ret2)
            #获取当前所在集群的Haproxy信息，获取失败直接返回
            ret3 = get_haproxy(self.haproxy)

            self.assert_successful(ret3)
            #获取创建服务需要的数据
            k8sFlannelData = data.ServiceData(self.k8s_host_service, self.namespace,
                                              settings.SERVICE_CLAAS_REGION[0],
                                              lb_type='haproxy', alb_name=self.haproxy, lb_id=ret3['haproxy_id'],
                                              volume_id=ret2['volume_id'], volume_name=self.gluster_name, envfile=self.k8s_envfile)
            #创建Host模式挂载环境变量文件和glustfs存储卷的服务
            ret4 = create_service(self.k8s_host_service, k8sFlannelData.k8s_host_service(),
                                  settings.SERVICE_CLAAS_REGION[0])
            if not ret4["success"]:
                delete_volume(ret2['volume_id'], self.gluster_name)
            self.assert_successful(ret4)
            #访问服务，及时失败也可以继续执行测试
            ret5 = access_service(self.k8s_host_service, self.haproxy)
            if not ret5['success']:
                test_flag = False
            # 验证环境变量是否添加进去 失败可以继续后面测试
            ret6 = exec_feature(self.k8s_host_service, self.namespace, command="env",
                                commands_string="key=value")
            if not ret6['success']:
                test_flag = False
            # 验证volume id是否一致
            ret7 = verify_volumes(self.k8s_host_service, ret2['volume_id'])
            if not ret7['success']:
                test_flag = False

            # 判断是否有Metrics 不阻塞后面的测试
            ret8 = get_metrics(self.k8s_host_service)
            if not ret8['success']:
                test_flag = False
            # 停止服务 如果失败block后面操作
            ret9 = stop_app(self.k8s_host_service)
            self.assert_successful(ret9)
            # 启动服务 如果失败block 后面操作
            ret10 = start_app(self.k8s_host_service, num=1)
            self.assert_successful(ret10)
            # scale up 服务，更新服务的数量和size，失败block后面操作
            ret11 = update_service(self.k8s_host_service, num=2, size="XS")
            self.assert_successful(ret11)
            # scale down 服务更新服务的数量和size  失败block后面操作
            ret12 = update_service(self.k8s_host_service, num=1, size="XXS")
            self.assert_successful(ret12)

            # check 服务的日志
            ret13 = get_logs(self.k8s_host_service)
            if not ret13['success']:
                test_flag = False

            ret14 = delete_app(self.k8s_host_service, settings.SERVICE_CLAAS_REGION[0])
            if not ret14['success']:
                test_flag = False
            #删除volume
            sleep(30)
            delete_volume(ret2['volume_id'], self.gluster_name)

            result =  {
                'success': test_flag,
                "create envfile ": ret1,
                "create glustfs volume": ret2,
                "get haproxy id ": ret3,
                "create service": ret4,
                "access service": ret5,
                "check envfile": ret6,
                "check volume": ret7,
                "check metrics": ret8,
                "stop service": ret9,
                "start service": ret10,
                "scale up": ret11,
                "scale down": ret12,
                "check log": ret13,
                "delete service": ret14
            }
            self.assert_successful(result)
            return result

    if settings.ENV != "private":
        @case
        def k8s_healthycheck__k8s_service(self):
            if self.haproxy:
                # 设置flag
                test_flag = True
                # 创建部署服务需要的ebs存储卷，创建失败直接返回
                ret1 = create_volume(self.ebs_name, 'ebs', 'gp2')
                self.assert_successful(ret1)
                # 获取当前所在集群的Haproxy信息，获取失败直接返回
                ret2 = get_haproxy(self.haproxy)

                self.assert_successful(ret2)
                # 获取创建服务需要的数据
                k8sFlannelData = data.ServiceData(self.k8s_healthycheck_service, self.namespace,
                                                  settings.SERVICE_CLAAS_REGION[0],
                                                  lb_type='haproxy', alb_name=self.haproxy, lb_id=ret2['haproxy_id'],
                                                  volume_id=ret1['volume_id'], volume_name=self.ebs_name)
                # 创建挂载ebs存储卷和添加健康检查的服务
                ret3 = create_service(self.k8s_healthycheck_service, k8sFlannelData.k8s_healthycheck_service(),
                                      settings.SERVICE_CLAAS_REGION[0])
                if not ret3["success"]:
                    delete_volume(ret1['volume_id'], self.ebs_name)
                self.assert_successful(ret3)
                # 访问服务，及时失败也可以继续执行测试
                ret4 = access_service(self.k8s_healthycheck_service, self.haproxy)
                if not ret4['success']:
                    test_flag = False
                # 验证volume id是否一致
                ret5 = verify_volumes(self.k8s_healthycheck_service, ret1['volume_id'])
                if not ret5['success']:
                    test_flag = False

                ret6 = delete_app(self.k8s_healthycheck_service, settings.SERVICE_CLAAS_REGION[0])
                if not ret6['success']:
                    test_flag = False
                #sleep 30s 保证volume变成可以删除的状态
                sleep(30)
                # 删除volume
                ret7 = delete_volume(ret1['volume_id'], self.ebs_name)

                result =  {
                    'success': test_flag,
                    "create ebs volume": ret1,
                    "get haproxy id ": ret2,
                    "create service": ret3,
                    "access service": ret4,
                    "check volume": ret5,
                    "delete service": ret6,
                    "delete volume": ret7
                }
                self.assert_successful(result)
                return result
    else:
        pass

    @case
    def ex_elb_service_test__k8s_service(self):
        test_flag = True
        #创建一个外网的ELB 失败返回
        ret1 = create_alb(self.k8s_external_elb, create_type='manual', type='elb', alb_region=settings.SERVICE_CLAAS_REGION[0])
        self.assert_successful(ret1)

        elb_data = data.ServiceData(self.k8s_exelb_service, settings.CLAAS_NAMESPACE, settings.SERVICE_CLAAS_REGION[0], lb_type='elb',
                                    alb_name=self.k8s_external_elb, lb_id=ret1['id'])
        #创建一个使用ELB网络模式的服务 失败返回
        ret2 = create_service(self.k8s_exelb_service, elb_data.k8s_exelb_service(), settings.SERVICE_CLAAS_REGION[0])
        self.assert_successful(ret2)
        #验证服务是否可以访问 失败继续测试
        # ret3 = access_service(self.k8s_exelb_service, self.k8s_external_elb)
        # if not ret3['success']:
        #     test_flag = False

        # 验证环境变量是否添加进去 失败可以继续后面测试
        ret4 = exec_feature(self.k8s_exelb_service, self.namespace, command="'/bin/ls /'")
        if not ret4['success']:
            test_flag = False
        # 判断是否有Metrics 不阻塞后面的测试
        ret5 = get_metrics(self.k8s_exelb_service)
        if not ret5['success']:
            test_flag = False
        # 停止服务 如果失败block后面操作
        ret6 = stop_app(self.k8s_exelb_service)
        self.assert_successful(ret6)
        # 启动服务 如果失败block 后面操作
        ret7 = start_app(self.k8s_exelb_service, num=1)
        self.assert_successful(ret7)
        # scale up 服务，更新服务的数量和size，失败block后面操作
        ret8 = update_service(self.k8s_exelb_service, num=2, size="XS")
        self.assert_successful(ret8)
        # scale down 服务更新服务的数量和size  失败block后面操作
        ret9 = update_service(self.k8s_exelb_service, num=1, size="XXS")
        self.assert_successful(ret9)

        # check 服务的日志
        # ret10 = get_logs(self.k8s_exelb_service)
        # if not ret10['success']:
        #     test_flag = False

        ret11 = delete_alb(self.k8s_external_elb)
        self.assert_successful(ret11)

        ret12 = delete_app(self.k8s_exelb_service)
        self.assert_successful(ret12)
        result = {
            'success': test_flag,
            "create elb": ret1,
            "create elb service": ret2,
            # "access service": ret3,
            "service exec ": ret4,
            "get metrics": ret5,
            "stop service": ret6,
            "start service": ret7,
            "scale up service": ret8,
            "scale down service": ret9,
            # "get logs": ret10,
            "delete elb": ret11,
            "delete service": ret12
        }
        self.assert_successful(result)
        return result

    @case
    def inner_elb_service_test__k8s_service(self):
        test_flag = True
        # 创建一个内网的ELB 失败返回
        ret1 = create_alb(self.k8s_internal_elb, create_type='manual', type='elb',
                                   alb_region=settings.SERVICE_CLAAS_REGION[0], address_type="internal")
        self.assert_successful(ret1)

        elb_data = data.ServiceData(self.k8s_innerelb_service, settings.CLAAS_NAMESPACE, settings.SERVICE_CLAAS_REGION[0],
                                    lb_type='elb',
                                    alb_name=self.k8s_internal_elb, lb_id=ret1['id'])
        # 创建一个使用ELB网络模式的服务 失败返回
        ret2 = create_service(self.k8s_innerelb_service, elb_data.k8s_innerelb_service(), settings.SERVICE_CLAAS_REGION[0])
        self.assert_successful(ret2)
        # 验证服务是否可以访问 失败继续测试
        ret3 = access_service(self.k8s_innerelb_service, self.k8s_internal_elb)
        if not ret3['success']:
            test_flag = False

        # 验证环境变量是否添加进去 失败可以继续后面测试
        ret4 = exec_feature(self.k8s_innerelb_service, self.namespace, command="'/bin/ls /'")
        if not ret4['success']:
            test_flag = False
        # 判断是否有Metrics 不阻塞后面的测试
        ret5 = get_metrics(self.k8s_innerelb_service)
        if not ret5['success']:
            test_flag = False
        # 停止服务 如果失败block后面操作
        ret6 = stop_app(self.k8s_innerelb_service)
        self.assert_successful(ret6)
        # 启动服务 如果失败block 后面操作
        ret7 = start_app(self.k8s_innerelb_service, num=1)
        self.assert_successful(ret7)
        # scale up 服务，更新服务的数量和size，失败block后面操作
        ret8 = update_service(self.k8s_innerelb_service, num=2, size="XS")
        self.assert_successful(ret8)
        # scale down 服务更新服务的数量和size  失败block后面操作
        ret9 = update_service(self.k8s_innerelb_service, num=1, size="XXS")
        self.assert_successful(ret9)

        # check 服务的日志
        # ret10 = get_logs(self.k8s_innerelb_service)
        # if not ret10['success']:
        #     test_flag = False

        ret11 = delete_alb(self.k8s_innerelb_service)
        self.assert_successful(ret11)

        ret12 = delete_app(self.k8s_innerelb_service)
        self.assert_successful(ret12)
        result = {
            'success': test_flag,
            "create elb": ret1,
            "create elb service": ret2,
            "access service": ret3,
            "service exec ": ret4,
            "get metrics": ret5,
            "stop service": ret6,
            "start service": ret7,
            "scale up service": ret8,
            "scale down service": ret9,
            # "get logs": ret10,
            "delete elb": ret11,
            "delete service": ret12
        }
        self.assert_successful(result)
        return result
