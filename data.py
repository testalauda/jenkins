import settings
from utils import get_registry_info, get_repo

class ServiceData(object):
   
    def __init__(self, service_name, namespace, region_name, mode='ELB', node_tag='', static_ip='', lb_type='haxpoxy',
                 alb_name='', lb_id='', config_name='', space_name=settings.SPACE_NAME, mipn_enabled=False, envfile='',
                 volume_id='', volume_name='', centificate_name='', centificate_id=''):
        self.service_name = service_name
        self.namespace = namespace
        self.region_name = region_name
        self.mode = mode
        self.node_tag = node_tag
        self.static_ip = static_ip
        self.lb_type = lb_type
        self.alb_name = alb_name
        self.lb_id = lb_id
        self.config_name = config_name
        self.space_name = space_name
        self.mipn_enabled = mipn_enabled
        self.envfile = envfile
        self.volume_id = volume_id
        self.volume_name = volume_name
        self.centificate_name = centificate_name
        self.centificate_id = centificate_id

    def get_image_registry(self):
        if settings.ENV == 'private':
            return get_registry_info().get("registry_url", settings.REGISTRY_URL)
        else:
            return settings.REGISTRY_URL

    def haproxy_bridge_service(self):
        new_service = {
            "service_name": "haproxybridge" + self.service_name,
            "health_checks": [],
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "vipertest/e2e")),
            "image_tag": settings.IMAGE_TAG,
            "instance_envvars": {"ENV": "TestEnv"},
            "instance_ports": [
                {
                   "container_port": 80,
                   "protocol": "tcp",
                   "endpoint_type": "http-endpoint"
                }
            ],
            "instance_size": "XXS",
            "linked_to_apps": "{}",
            "load_balancer_choice": "ENABLE",
            "load_balancers": [],
            "namespace": self.namespace,
            "network_mode": "BRIDGE",
            "region_name": self.region_name,
            "scaling_mode": "MANUAL",
            "service_mode": "SINGLEqw",
            "target_num_instances": 1,
            "target_state": "STARTED",
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def haproxy_host_service(self):
        new_service = {
            "service_name": "proxyhost" + self.service_name,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "vipertest/e2e")),
            "image_tag": settings.IMAGE_TAG,
            "region_name": self.region_name,
            "instance_size": "XXS",
            "network_mode": "HOST",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "required_ports": [80],
            "envfiles": [{"name": "notDelete"}],
            "load_balancers": [],
            "instance_ports": [
                {
                   "container_port": 80,
                   "protocol": "tcp",
                   "endpoint_type": "http-endpoint"
                }
            ],
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def rawcontainer_bridge_service(self):
        new_service = {
            "service_name": "rb" + self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "tutum/ubuntu")),
            "image_tag": settings.IMAGE_TAG,
            "region_name": self.region_name,
            "instance_size": "XXS",
            "network_mode": "BRIDGE",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "required_ports": [22],
            "load_balancers": [],
            "instance_ports":[],
            "space_name": settings.SPACE_NAME
        }
        return new_service
    
    def rawcontainer_host_service(self):
        new_service = {
            "service_name": "rh" + self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "tutum/mysql")),
            "image_tag": settings.IMAGE_TAG,
            "region_name": self.region_name,
            "instance_size": "XS",
            "network_mode": "HOST",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "required_ports": [3306],
            "load_balancers": [],
            "instance_ports":[],
            "space_name": settings.SPACE_NAME
        }
        return new_service
    
    def elb_host_internal_service(self):
        new_service = {
            "service_name": "ehi" + self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "tutum/tomcat")),
            "image_tag": "latest",
            "region_name": self.region_name,
            "instance_size": "XS",
            "network_mode": "HOST",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "required_ports": [8080],
            "load_balancers": [
                {
                  "type": self.mode,
                  "is_internal": "true",
                  "listeners": [
                        {
                          "protocol": "HTTP",
                          "lb_port": 8080,
                          "container_port": 8080
                        }
                    ]
                }
            ],
            "instance_ports":[],
            "space_name": settings.SPACE_NAME
        }
        return new_service
    
    def elb_host_external_service(self):
        new_service = {
            "service_name": "ehe" + self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "library/nginx")),
            "image_tag": "latest",
            "region_name": self.region_name,
            "instance_size": "XXS",
            "network_mode": "HOST",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "required_ports": [80],
            "instance_envvars": {"ENV": "TestEnv"},
            "load_balancers": [
                {
                    "type": self.mode,
                    "is_internal": False,
                    "listeners": [
                        {
                        "protocol": "HTTP",
                        "lb_port": 80,
                        "container_port": 80
                        }
                    ]
                }
            ],
            "instance_ports":[],
            "space_name": settings.SPACE_NAME
        }
        return new_service
    
    def elb_bridge_internal_service(self):
        new_service = {
            "service_name": "ebi" + self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "tutum/tomcat")),
            "image_tag": "latest",
            "region_name": self.region_name,
            "instance_size": "XS",
            "network_mode": "BRIDGE",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "load_balancers": [
                {
                  "type": self.mode,
                  "is_internal": "true",
                  "listeners": [
                    {
                      "protocol": "HTTP",
                      "lb_port": 8080,
                      "container_port": 8080
                    }
                  ]
                }
            ],
            "instance_ports":[],
            "space_name": settings.SPACE_NAME
        }
        return new_service
    
    def elb_bridge_external_service(self):
        new_service = {
            "service_name": "elbbridge" + self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "library/nginx")),
            "image_tag": "latest",
            "region_name": self.region_name,
            "instance_size": "XXS",
            "network_mode": "BRIDGE",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "instance_envvars": {"ENV": "TestEnv"},
            "load_balancers": [
                {
                    "type": self.mode,
                    "is_internal": False,
                    "listeners": [
                        {
                            "protocol": "HTTP",
                            "lb_port": 80,
                            "container_port": 80
                        }
                    ]
                }
            ],
            "instance_ports": [],
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def heathy_check_service(self):
        new_service = {
            "image_tag": "latest", 
            "region_name": self.region_name, 
            "service_name": "heathy-check" + self.service_name, 
            "instance_size": "XXS", 
            "scaling_mode": "MANUAL", 
            "namespace": self.namespace, 
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "network_mode": "BRIDGE",
            "target_state": "STARTED", 
            "health_checks": [{
                "protocol": "HTTP",
                "ignore_http1xx": False, 
                "timeout_seconds": 20,
                "interval_seconds": 20,
                "max_consecutive_failures": 10, 
                "path": "/",
                "port": 80, 
                "grace_period_seconds": 100
                }], 
            "instance_envvars": {}, 
            "load_balancers": [{
                "listeners": [{
                    "container_port": 80,
                    "protocol": "HTTP",
                    "lb_port": 80
                    }], 
                "is_internal": False, 
                "type": self.mode, 
                "_network_type": "external"
                }], 
            "target_num_instances": 1,
            "space_name": settings.SPACE_NAME
        }
        return new_service
    
    def node_tag_service(self):
        new_service = {
            "region_name": self.region_name,
            "service_name": "test-node",
            "instance_size": "XXS",
            "scaling_mode": "MANUAL",
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "network_mode": "BRIDGE",
            "target_state": "STARTED",
            "instance_ports": [
                {
                    "ipaddress": "sharedip",
                    "service_port": 80,
                    "endpoint_type": "http-endpoint",
                    "protocol": "tcp",
                    "container_port": 80
                }
            ],
            "target_num_instances": 1,
            "node_tag": self.node_tag,
            "space_name": settings.SPACE_NAME
            }
        return new_service

    def internal_haproxy(self):
        new_service = {
            "target_num_instances": 1,
            "service_name": "redis1",
            "linked_to_apps": "{}",
            "region_name": self.region_name,
            "instance_size": "XXS",
            "scaling_mode": "MANUAL",
            "namespace": self.namespace,
            "network_mode": "BRIDGE",
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "library/redis")),
            "image_tag": settings.IMAGE_TAG,
            "target_state": "STARTED",
            "instance_ports": [
                {
                    "ipaddress": "sharedip",
                    "service_port": 6379,
                    "endpoint_type": "internal-endpoint",
                    "protocol": "tcp",
                    "container_port": 6379
                }

            ],
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def link_service(self):
        new_service = {
            "target_num_instances": 1,
            "service_name": "web1",
            "linked_to_apps": "{\"redis1\":\"REDIS\"}",
            "instance_size": "XXS",
            "region_name": self.region_name,
            "scaling_mode": "MANUAL",
            "namespace": self.namespace,
            "image_name": "{}/alauda/flask-redis".format(settings.REGISTRY_URL),
            "network_mode": "BRIDGE",
            "target_state": "STARTED",
            "instance_ports": [
                {
                    "ipaddress": "sharedip",
                    "service_port": 80,
                    "endpoint_type": "http-endpoint",
                    "protocol": "tcp",
                    "container_port": 80
                }
            ],
            "image_tag": "latest",
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def volume_logfile_service(self):
        new_service = {
            "image_tag": "v1",
            "region_name": self.region_name,
            "service_name": self.service_name,
            "instance_size": "XXS",
            "scaling_mode": "MANUAL",
            "namespace": self.namespace,
            "image_name": "index-staging.alauda.cn/testorg001/volume-test",
            "network_mode": "FLANNEL",
            "target_state": "STARTED",
            "instance_envvars": {
                "__ALAUDA_FILE_LOG_PATH__": "/home/*.txt"
            },
            "volumes": [
                {
                    "app_volume_dir": "/var/lib/mysql",
                    "volume_id": "host_path",
                    "volume_name": "/var/log/"
                }
            ],
            "target_num_instances": 1,
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def static_ip_service(self):
        new_service =  {
            "region_name": self.region_name,
            "service_name": self.service_name,
            "instance_size": "XXS",
            "scaling_mode": "MANUAL",
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "library/redis")),
            "image_tag": settings.IMAGE_TAG,
            "network_mode": "STATIC_IP",
            "target_state": "STARTED",
            "instance_envvars": {},
            "private_ip": self.static_ip,
            "target_num_instances": 1,
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def alb_service(self):
        new_service = {
            "region_name": self.region_name,
            "service_name": self.service_name,
            "instance_size": "XXS",
            "scaling_mode": "MANUAL",
            "namespace": settings.CLAAS_NAMESPACE,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "network_mode": "BRIDGE",
            "target_state": "STARTED",
            "instance_envvars": {},
            "mipn_enabled": self.mipn_enabled,
            "version": "v2",
            "load_balancers": [
                {
                    "listeners": [
                    {
                        "container_port": 80,
                        "protocol": "http",
                        "listener_port": 80
                    }
                    ],
                "type": self.lb_type,
                "name": self.alb_name,
                "load_balancer_id": self.lb_id
                }
            ],
            "target_num_instances": 1,
            "ports": [80],
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def config_service(self):
        new_service = {
            "service_name": self.service_name,
            "health_checks": [],
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "instance_size": "XXS",
            "linked_to_apps": "{}",
            "load_balancer_choice": "ENABLE",
            "load_balancers": [],
            "namespace": self.namespace,
            "network_mode": "BRIDGE",
            "region_name": self.region_name,
            "scaling_mode": "MANUAL",
            "service_mode": "SINGLE",
            "target_num_instances": 1,
            "target_state": "STARTED",
            "mount_points": [
                {
                    "path": "/home/config_path",
                    "type": "config",
                    "value": {
                        "name": self.config_name,
                        "key": "name2"
                    }
                }
            ],
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def quota_service(self):
        new_service = {
            "service_name": self.service_name,
            "health_checks": [],
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "instance_ports": [],
            "instance_size": "XXS",
            "linked_to_apps": "{}",
            "load_balancer_choice": "ENABLE",
            "load_balancers": [],
            "namespace": self.namespace,
            "network_mode": "FLANNEL",
            "region_name": self.region_name,
            "scaling_mode": "MANUAL",
            "service_mode": "SINGLE",
            "target_num_instances": 1,
            "target_state": "STARTED",
            "space_name": self.space_name
        }
        return new_service

    def k8s_flannel_service(self):
        new_service = {
            "service_name": self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), self.namespace+ "/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "region_name": self.region_name,
            "instance_size": "XXS",
            "network_mode": "FLANNEL",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "mipn_enabled": self.mipn_enabled,
            "ports": [
                80
            ],
            "instance_envvars": {
                "k8s_key": "k8s_value",
                "__ALAUDA_FILE_LOG_PATH__": "/home/*.txt"

            },
            "load_balancers": [
                {
                    "type": self.lb_type,
                    "version": 1,
                    "name": self.alb_name,
                    "load_balancer_id": self.lb_id,
                    "listeners":[
                        {
                            "protocol": "http",
                            "listener_port": 80,
                            "container_port": 80,
                            "rules": []
                        }
                    ]
                }
            ],
            "mount_points": [
                {
                    "path": "/home/abc",
                    "type": "raw",
                    "value": "config"
                }
            ],
            "node_selector": {
                "ip": self.node_tag
            },
            "volumes": [
                {
                    "app_volume_dir": "/var/log/",
                    "volume_id": "host_path",
                    "volume_name": "/var/log"
                }
            ],
            "instance_ports": [],
            "space_name": self.space_name,
            "version": "v2"
        }
        return new_service

    def k8s_host_service(self):
        new_service = {
            "service_name": self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "region_name": self.region_name,
            "instance_size": "XXS",
            "network_mode": "HOST",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "envfiles": [{"name": self.envfile}],
            "ports": [
                80
            ],
            "instance_envvars": {},
            "load_balancers": [
                {
                    "type": self.lb_type,
                    "name": self.alb_name,
                    "load_balancer_id": self.lb_id,
                    "listeners":[
                        {
                            "protocol": "http",
                            "lb_port": 80,
                            "container_port": 80,
                            "domains": []
                        }
                    ]
                }
            ],
            "volumes": [
                {
                    "app_volume_dir": "/var/log/",
                    "volume_id": self.volume_id,
                    "volume_name": self.volume_name
                }
            ],
            "instance_ports": [],
            "space_name": self.space_name,
            "version": "v2"
        }
        return new_service

    def k8s_healthycheck_service(self):
        new_service = {
            "service_name": self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "region_name": self.region_name,
            "instance_size": "XXS",
            "network_mode": "FLANNEL",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "ports": [
                80
            ],
            "instance_envvars": {},
            "load_balancers": [
                {
                    "type": self.lb_type,
                    "name": self.alb_name,
                    "load_balancer_id": self.lb_id,
                    "listeners":[
                        {
                            "protocol": "http",
                            "lb_port": 80,
                            "container_port": 80,
                            "domains": []
                        }
                    ]
                }
            ],
            "volumes": [
                {
                    "app_volume_dir": "/var/log/",
                    "volume_id": self.volume_id,
                    "volume_name": self.volume_name
                }
            ],
            "health_checks": [{
                "protocol": "HTTP",
                "ignore_http1xx": False,
                "timeout_seconds": 20,
                "interval_seconds": 20,
                "max_consecutive_failures": 10,
                "path": "/",
                "port": 80,
                "grace_period_seconds": 100
            }],
            "instance_ports": [],
            "space_name": self.space_name,
            "version": "v2"
        }
        return new_service

    def k8s_exelb_service(self):
        new_service = {
            "region_name": self.region_name,
            "service_name": self.service_name,
            "instance_size": "XXS",
            "scaling_mode": "MANUAL",
            "namespace": settings.CLAAS_NAMESPACE,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "network_mode": "HOST",
            "target_state": "STARTED",
            "instance_envvars": {},
            "mipn_enabled": self.mipn_enabled,
            "version": "v2",
            "load_balancers": [
                {
                    "listeners": [
                    {
                        "container_port": 800,
                        "protocol": "http",
                        "listener_port": 800
                    }
                    ],
                "type": self.lb_type,
                "name": self.alb_name,
                "load_balancer_id": self.lb_id
                }
            ],
            "target_num_instances": 1,
            "ports": [80],
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def k8s_innerelb_service(self):
        new_service = {
            "region_name": self.region_name,
            "service_name": self.service_name,
            "instance_size": "XXS",
            "scaling_mode": "MANUAL",
            "namespace": settings.CLAAS_NAMESPACE,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "network_mode": "FLANNEL",
            "target_state": "STARTED",
            "instance_envvars": {},
            "mipn_enabled": self.mipn_enabled,
            "version": "v2",
            "load_balancers": [
                {
                    "listeners": [
                    {
                        "container_port": 80,
                        "protocol": "http",
                        "listener_port": 80
                    }
                    ],
                "type": self.lb_type,
                "name": self.alb_name,
                "load_balancer_id": self.lb_id
                }
            ],
            "target_num_instances": 1,
            "ports": [80],
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def ha_heathy_check_service(self):
        new_service = {
            "image_tag": "latest",
            "region_name": self.region_name,
            "service_name": self.service_name,
            "instance_size": "XXS",
            "scaling_mode": "MANUAL",
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "network_mode": "BRIDGE",
            "target_state": "STARTED",
            "health_checks": [{
                "protocol": "HTTP",
                "ignore_http1xx": False,
                "timeout_seconds": 20,
                "interval_seconds": 20,
                "max_consecutive_failures": 10,
                "path": "/",
                "port": 80,
                "grace_period_seconds": 100
                }],
            "instance_envvars": {},
            "instance_ports": [
                {"ipaddress": "sharedip", "service_port": 80, "endpoint_type": "http-endpoint", "protocol": "tcp",
                 "container_port": 80}],
            "target_num_instances": 1,
            "mipn_enabled": "True",
            "space_name": settings.SPACE_NAME
        }
        return new_service

    def https_service(self):
        new_service = {
            "service_name": self.service_name,
            "namespace": self.namespace,
            "image_name": "{}/{}".format(self.get_image_registry(), get_repo().get(("service_repo"), "alauda/hello-world")),
            "image_tag": settings.IMAGE_TAG,
            "region_name": self.region_name,
            "instance_size": "XXS",
            "network_mode": "FLANNEL",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "target_num_instances": 1,
            "ports": [
                80
            ],
            "instance_envvars": {},
            
                    "version": 23
                }
            ],
            "space_name": self.space_name,
            "version": "v2"
        }
        return new_service
