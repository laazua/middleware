"""
全局变量定义文件
这些变量会应用到所有节点
"""

## pyinfra预定义变量
## 显示配置,会应用到所有operations上
_sudo = True

# Elasticsearch 运行用户和组
es_user = "elastic"
es_group = "elastic"

# JDK 相关配置
jdk_version = "jdk-17.0.2"
jdk_package = "openjdk-17.0.2_linux-x64_bin.tar.gz"
jdk_install_path = f"/usr/local/{jdk_version}"

# Elasticsearch 相关配置
elastic_version = "elasticsearch-9.1.1"
elastic_package = "elasticsearch-9.1.1-linux-x86_64.tar.gz"
elastic_install_path = "/usr/local"
elastic_work_path = f"{elastic_install_path}/{elastic_version}"
elastic_cluster_name = "es-cluster"
elastic_data_path = "/var/lib/elastic"
elastic_log_path = "/var/log/elastic"
elastic_pid_path = "/var/run/elastic"
elastic_http_port = 9200

# kibana 运行用户和组
kb_user = "kibana"
kb_group = "kibana"

# Kibana 相关配置
kibana_version = "kibana-9.1.1"
kibana_package = "kibana-9.1.1-linux-x86_64.tar.gz"
kibana_install_path = "/usr/local"
kibana_work_path = f"{kibana_install_path}/{kibana_version}"
kibana_data_path = "/var/lib/kibana"
kibana_log_path = "/var/log/kibana"
kibana_pid_path = "/var/run/kibana"
kibana_http_port = 5601
kibana_http_host = "192.168.165.87"