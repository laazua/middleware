# 入口文件
from pyinfra import host
from pyinfra.api import deploy

from tasks import setup
from tasks import elastic
from tasks import kibana


# 初始化 Elasticsearch 节点
@deploy('SetUp Elasticsearch Nodes')
def initialize_elastic_nodes():
    # 当前主机是 es 节点才执行
    if host.name in host.group_data.get("es_node_ips", []):
        setup.elastic_user()
        setup.swap()
        setup.selinux()
        setup.ulimit()
        setup.sysctl()
        setup.timezone()
        setup.firewalld()
        setup.tools()
        setup.openjdk()


# 部署 Elasticsearch 集群
@deploy('Deploy Elasticsearch Cluster')
def deploy_elastic_cluster():
    # 当前主机是 es 节点才执行
    if host.name in host.group_data.get("es_node_ips", []):
        elastic.install()
        elastic.configure()
        elastic.service()


# 部署 Kibana
@deploy('Deploy Kibana')
def deploy_kibana():
    # 当前主机是 kb 节点才执行
    if host.name in host.group_data.get("kb_node_ips", []):
        kibana.kibana_user()
        kibana.install()
        kibana.configure()
        kibana.timezone()
        kibana.service()


# Elastic 部署
if host.data.get('es'):
    initialize_elastic_nodes()
    deploy_elastic_cluster()


# Kibana 部署
if host.data.get('kb'):
    deploy_kibana()