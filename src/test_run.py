import logging

from brewmaster.run import TestRunner

from CLaaS.Alarms import AlarmTest
from CLaaS.application import ApplicationTest
from CLaaS.bridgeMode import bridgeModeServiceTest
from CLaaS.catalog import CatalogTest
from CLaaS.cifactory import CIFactoryTest
from CLaaS.cluster import ClusterTest
from CLaaS.cmp import CMPTest
from CLaaS.configurations import ConfigurationsTest
from CLaaS.env import EnvfileTest
from CLaaS.heathycheck import healthyCheckTest
from CLaaS.hostMode import hostModeServiceTest
from CLaaS.internal_endpoint import internalEndpointServiceTest
from CLaaS.node_tag import nodeTagServiceTest
from CLaaS.notification import NotificationTest
from CLaaS.pipeline import PipelineTest
from CLaaS.privatebuild import PrivatebuildTest
from CLaaS.privaterepo import PrivateRepoTest
from CLaaS.profile import ProfileTest
from CLaaS.publicrepo import RepoTest
from CLaaS.quota import QuotaTest
from CLaaS.stateLogfileService import stateLogfileServiceTest
from CLaaS.sync_image import SyncImageTest
from CLaaS.template import AppTemplateTest
from CLaaS.volumes import VolumeTest
from CLaaS.dashboard import DashboardTest
from CLaaS.alb_region import NetworkTest
from CLaaS.ldap import LDAPTest
from rbac.rbac_env import RbacEnvTest
from rbac.rbac_template import RbactemplateTest
from rbac.rbac_quota import RbacQuotaTest
from rbac.rbac_notification import RbacnotificationTest
from rbac.rbac_static_ip import RbacipTest
from rbac.rbac_configuration import RbacconfigurationTest
from rbac.rbac_privaterepo import RbacrepositoryTest
from rbac.rbac_service import RbacserviceTest
from rbac.rbac_volume import RbacvolumeTest
from rbac.rbac_role import RbacRoleTest
from rbac.rbac_subaccount import RbacsubaccountTest
from rbac.rbac_cluster import RbacClusterTest
from CLaaS.k8s_region import K8sServiceTest
from CLaaS.job import JOBTest
from CLaaS.https import CetificateTest
from CLaaS.Alarmsv2 import alarmv2Test
from CLaaS.log import logTest
from CLaaS.integration import integrationTest
from CLaaS.load_balancers import load_balanersTest
import settings
import logging
import data
from utils import get_region_data

logger = logging.getLogger()

# class ClaasTest(TestRunner,nodeTagServiceTest, bridgeModeServiceTest, hostModeServiceTest, healthyCheckTest,
#                 ApplicationTest, NotificationTest, PrivatebuildTest, PrivateRepoTest, AppTemplateTest, AlarmTest,
#                 EnvfileTest, stateLogfileServiceTest, RepoTest, ProfileTest, CatalogTest, CMPTest, PipelineTest,
#                 internalEndpointServiceTest, VolumeTest, ClusterTest, CIFactoryTest, ConfigurationsTest, DashboardTest,
#                 QuotaTest, SyncImageTest, RbacRoleTest, RbacvolumeTest, RbacserviceTest, NetworkTest, K8sServiceTest,
#                 RbacrepositoryTest, RbacconfigurationTest, RbacipTest, RbacnotificationTest, RbacQuotaTest,
#                 RbactemplateTest, RbacEnvTest, RbacClusterTest, RbacsubaccountTest, JOBTest, LDAPTest,alarmv2Test,
#                 logTest, CetificateTest, integrationTest):

class ClaasTest(TestRunner,load_balanersTest):

# class ClaasTest(TestRunner, CetificateTest):

    name = 'claas-cd-e2e'

    app_region = settings.SERVICE_CLAAS_REGION[0]

    def set_up(self):
        self.data = {}
        self.region_data = {}
        self.region_data = get_region_data(self.app_region)


        # self.repo_set_up()
        # self.profile_set_up()
        # self.alarm_set_up()
        # self.envfile_set_up()
        # self.notification_set_up()
        # self.app_template_set_up()
        # self.application_set_up()
        # self.private_build_set_up()
        # self.private_repo_set_up()
        # self.bridge_mode_service_set_up()
        # self.host_mode_service_set_up()
        # self.healthy_check_set_up()
        # self.node_tag_service_set_up()
        # self.internal_endpoint_set_up()
        # self.state_logfile_set_up()
        # self.volume_set_up()
        # self.catalog_set_up()
        # self.cmp_set_up()
        # self.pipeline_set_up()
        # self.cluster_set_up()
        # self.cifactory_set_up()
        # self.network_set_up()
        # self.configuration_set_up()
        # self.dashboard_set_up()
        # self.quota_set_up()
        # self.syncimage_set_up()
        # self.rbac_env_set_up()
        # self.rbac_template_set_up()
        # self.rbac_quota_set_up()
        # self.rbac_notification_set_up()
        # self.rbac_ip_set_up()
        # self.rbac_configuration_set_up()
        # self.rbac_cluster_set_up()
        # self.rbac_repository_set_up()
        # self.rbac_service_set_up()
        # self.rbac_volume_set_up()
        # self.rbac_role_set_up()
        # self.rbac_subaccount_set_up()
        # self.k8s_service_set_up()
        # self.job_set_up()
        # self.ldap_set_up()
        # self.alarmv2_set_up()
        # self.log_set_up()
        # self.cetificate_set_up()
        # self.integration_set_up()
        self.load_balaners_set_up()

    def tear_down(self):
        # self.repo_tear_down()
        # self.profile_tear_down()
        # self.alarm_tear_down()
        # self.envfile_tear_down()
        # self.notification_tear_down()
        # self.app_template_tear_down()
        # self.application_tear_down()
        # self.private_build_tear_down()
        # self.private_repo_tear_down()
        # self.bridge_mode_service_tear_down()
        # self.host_mode_service_tear_down()
        # self.healthy_check_tear_down()
        # self.node_tag_service_tear_down()
        # self.internal_endpoint_tear_down()
        # self.state_logfile_tear_down()
        # self.volume_tear_down()
        # self.catalog_tear_down()
        # self.cmp_tear_down()
        # self.pipeline_tear_down()
        # self.cluster_tear_down()
        # self.cifactory_tear_down()
        # self.network_tear_down()
        # self.configuration_tear_down()
        # self.dashboard_tear_down()
        # self.quota_tear_down()
        # self.syncimage_tear_down()
        # self.rbac_env_tear_down()
        # self.rbac_template_tear_down()
        # self.rbac_quota_tear_down()
        # self.rbac_notification_tear_down()
        # self.rbac_ip_tear_down()
        # self.rbac_configuration_tear_down()
        # self.rbac_cluster_tear_down()
        # self.rbac_repository_tear_down()
        # self.rbac_service_tear_down()
        # self.rbac_volume_tear_down()
        # self.rbac_role_tear_down()
        # self.rbac_subaccount_tear_down()
        # self.k8s_service_tear_down()
        # self.job_tear_down()
        # self.ldap_tear_down()
        # self.alarmv2_tear_down()
        # self.log_tear_down()
        # self.cetificate_tear_down()
        # self.integration_tear_down()
        self.load_balaners_tear_down()

    def assert_successful(self, response):
        msg = response.get('message', response.get('total', response))
        print msg
        self.assertTrue(response['success'], msg=msg)
        return response

    def assert_successful_name(self, response, name):
        msg = "[[" + "Test Case:" + name + "]]." + " " + str(response.get('message', response.get('total', None)))
        print msg
        self.assertTrue(response['success'], msg=msg)
        return response
