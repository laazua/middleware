"""
Docstring for kafka.group_data.all
"""
_sudo = True

openjdk_pkg = 'openjdk-17.0.2_linux-x64_bin.tar.gz'
openjdk_install_path = '/usr/local'
openjdk_home_path = f'{openjdk_install_path}/jdk-17.0.2'

kfk_user = 'kafka'
kfk_group = 'kafka'
kfk_version = '2.13-4.1.1'
kfk_install_path = '/usr/local'
kfk_package_name = f'kafka_{kfk_version}.tgz'
kfk_work_path = f'{kfk_install_path}/kafka_{kfk_version}'
kfk_data_path = '/var/lib/kafka'
kfk_log_path = '/var/log/kafka'

controller_quorum_voters = '1@192.168.165.71:9093,2@192.168.165.72:9093,3@192.168.165.73:9093'

cluster_id = 'C_V4rzemStO-PHN29tWHVw'