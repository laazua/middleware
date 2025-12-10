from pyinfra import host
from pyinfra.operations import files, server


# 新建 kibana 运行用户和组: kibana
def kibana_user():
    kb_user = host.data.get('kb_user', 'kibana')
    kb_group = host.data.get('kb_group', 'kibana')
    server.group(
        name=f"Add User: {kb_user}",
        group=kb_group,
        system=True,
        # _sudo=True,
    )
    server.user(
        name=f"Add Group: {kb_group}",
        user=kb_user,
        system=True,
        create_home=False,
        group=kb_group,
        shell='/sbin/nologin',
        # _sudo=True,
    )


# 安装 kibana
def install():
    kibana_package = host.data.get("kibana_package")
    kibana_install_path = host.data.get("kibana_install_path")
    files.put(
        f"files/{kibana_package}",
        f"/tmp/{kibana_package}",
    )
    server.shell(
        name="Unpack Kibana package",
        commands=[f"tar -zxvf /tmp/{kibana_package} -C {kibana_install_path}"],
    )


# 配置 kibana 服务配置
def configure():
    kibana_work_path = host.data.get("kibana_work_path")
    kibana_data_path = host.data.get("kibana_data_path")
    kibana_log_path = host.data.get("kibana_log_path")
    kibana_pid_path = host.data.get("kibana_pid_path")
    files.template(
        src="templates/kibana.yml.j2",
        dest=f"{kibana_work_path}/config/kibana.yml",
        mode="644",
    )
    server.shell(
        name="Create Data, Log, and PID Directories for Kibana",
        commands=[
            f"mkdir -p {kibana_data_path} {kibana_log_path} {kibana_pid_path}",
            f"chown -R {host.data.get('kb_user')}:{host.data.get('kb_group')} {kibana_data_path} {kibana_log_path} {kibana_pid_path} {kibana_work_path}",
        ],
    )
    # 上传ca证书
    files.put(
        "files/ca.zip",
        f"{kibana_work_path}/config/ca.zip",
    )
    # 上传客户端证书
    files.put(
        "files/client.zip",
        f"{kibana_work_path}/config/client.zip",
    )
    server.shell(
        name="Generate SSL Certificates for Kibana",
        commands=[
            f"unzip -o {kibana_work_path}/config/ca.zip -d {kibana_work_path}/config/certs",
            f"unzip -o {kibana_work_path}/config/client.zip -d {kibana_work_path}/config/certs",
            f"chown -R {host.data.get('kb_user')}:{host.data.get('kb_group')} {kibana_work_path}/config/certs",
        ],
    )

# 配置 kibana systemd 服务
def service():
    files.template(
        name="Setup Kibana Systemd Service",
        src="templates/kibana.service.j2",
        dest="/etc/systemd/system/kibana.service",
    )
    server.shell(
        name="Reload systemd and enable Kibana service",
        commands=[
            "systemctl daemon-reload",
            "systemctl enable kibana.service",
            "systemctl start kibana.service",
        ],
    )



# 设置各个节点时区和时间同步
def timezone():
    server.shell(
        name="Setup Timezone",
        commands=["timedatectl set-timezone Asia/Shanghai"],
        # _sudo=True,
    )
    server.shell(
        name="Start and Enable Chronyd",
        commands=[
            "systemctl restart chronyd",
        ],
        _sudo=True,
    )
    

# 将kibana服务放行防火墙
def firewall():
    kb_http_port = host.data.get("kibana_http_port", 5601)
    server.shell(
        name="Allow Kibana HTTP Port in Firewall",
        commands=[
            f"firewall-cmd --permanent --add-port={kb_http_port}/tcp",
            "firewall-cmd --reload",
        ],
    )