from pyinfra import host
from pyinfra.operations import files, server


# 安装 elasticsearch
def install():
    elastic_package = host.data.get("elastic_package")
    elastic_install_path = host.data.get("elastic_install_path")
    files.put(
        f"files/{elastic_package}",
        f"/tmp/{elastic_package}",
    )
    server.shell(
        name="Unpack elasticsearch package",
        commands=[f"tar -zxvf /tmp/{elastic_package} -C {elastic_install_path}"],
    )


# 配置 elasticsearch 服务配置
def configure():
    elastic_work_path = host.data.get("elastic_work_path")
    elastic_data_path = host.data.get("elastic_data_path")
    elastic_log_path = host.data.get("elastic_log_path")
    elastic_pid_path = host.data.get("elastic_pid_path")
    files.template(
        src="templates/elasticsearch.yml.j2",
        dest=f"{elastic_work_path}/config/elasticsearch.yml",
        mode="644",
    )
    files.template(
        src="templates/jvm.options.j2",
        dest=f"{elastic_work_path}/config/jvm.options",
        mode="644",
    )
    server.shell(
        name="Create Data, Log, and PID Directories",
        commands=[
            f"mkdir -p {elastic_data_path} {elastic_log_path} {elastic_pid_path}",
            f"chown -R {host.data.get('es_user')}:{host.data.get('es_group')} {elastic_data_path} {elastic_log_path} {elastic_pid_path} {elastic_work_path}",
        ],
    )
    files.put(
        "files/ca.zip",
        f"{elastic_work_path}/config/ca.zip",
    )
    server.shell(
        name="Generate SSL Certificates",
        commands=[
            f"unzip -o {elastic_work_path}/config/ca.zip -d {elastic_work_path}/config/certs",
            f"rm -f {elastic_work_path}/config/certs/node.zip",
            f"echo '\n' | {elastic_work_path}/bin/elasticsearch-certutil cert --ca-cert {elastic_work_path}/config/certs/ca/ca.crt --ca-key {elastic_work_path}/config/certs/ca/ca.key --ip {host.name} --dns localhost --out {elastic_work_path}/config/certs/node.zip --pem",
            f"unzip -o {elastic_work_path}/config/certs/node.zip -d {elastic_work_path}/config/certs",
            f"chown -R {host.data.get('es_user')}:{host.data.get('es_group')} {elastic_work_path}/config/certs",
        ],
    )

# 配置 elastic systemd 服务
def service():
    files.template(
        name="Setup Elastic Systemd Service",
        src="templates/elastic.service.j2",
        dest="/etc/systemd/system/elastic.service",
        mode="644",

    )
    server.shell(
        name="Reload Systemd Daemon",
        commands=[
        "systemctl daemon-reload",
        "systemctl enable elastic.service",
        "systemctl start elastic.service",
        ],
    )
