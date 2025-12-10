import pyinfra
from pyinfra.operations import server, files


@pyinfra.api.deploy('Run Node Setup')
def run():
    user = pyinfra.host.data.get('kafka_user', 'kafka')
    group = pyinfra.host.data.get('kafka_group', 'kafka')
    
    server.group(
        name=f"Add Group: {group}",
        group=group,
        system=True,
        # _sudo=True,
    )

    server.user(
        name=f"Add User: {user}",
        user=user,
        system=True,
        create_home=False,
        group=group,
        shell='/sbin/nologin',
        # _sudo=True,
    )

    kfk_data_path = pyinfra.host.data.get('kafka_data_path', '/var/lib/kafka')
    kfk_log_path = pyinfra.host.data.get('kafka_log_path', '/var/log/kafka')
    server.shell(
        name="Create Kafka Directories",
        commands=[
            f"mkdir -p {kfk_data_path} {kfk_log_path}",
            f"chown -R {user}:{group} {kfk_data_path} {kfk_log_path}",    
        ]
    )

    # 安装必要命令
    server.packages(
        name="Install Required Packages",
        packages=['tar.x86_64'],
        # _sudo=True,
    )

    # 上传jdk包
    openjdk_install_path = pyinfra.host.data.get('openjdk_install_path', '/usr/local')
    openjdk_pkg = pyinfra.host.data.get('openjdk_pkg', 'openjdk-17.0.2_linux-x64_bin.tar.gz')
    openjdk_home_path = pyinfra.host.data.get('openjdk_home_path', f'{openjdk_install_path}/jdk-17.0.2')
    files.put(
        f"files/{openjdk_pkg}",
        f"/tmp/{openjdk_pkg}",
        # _sudo=True,
    )
    # 解压 JDK 包
    server.shell(
        name="Extract JDK Package",
        commands=[f"tar -zxvf /tmp/{openjdk_pkg} -C {openjdk_install_path}"],
        _sudo=True,
    )
    # 配置环境变量
    files.block(
        name="Set JDK Environment Variables",
        path="/etc/profile.d/jdk.sh",
        content=f"""export JAVA_HOME={openjdk_home_path}
export PATH=$PATH:{openjdk_home_path}/bin
""",
        # _sudo=True,
    )
    server.shell(
        name="Load JDK Environment Variables",
        commands=["source /etc/profile.d/jdk.sh"],
        # _sudo=True,
    )

    # 关闭 SELinux
    server.shell(
        name="Disable SELinux",
        commands=[
            "setenforce 0",
            "sed -e 's|^SELINUX=enforcing|SELINUX=disabled|' -i.bak /etc/selinux/config"
        ],
        # _sudo=True,
    )
    
    # 防火墙配置
    ip_white_list = pyinfra.host.group_data.get('ip_white_list', [])
    if not ip_white_list:
        print("No IP white list found, skipping firewall configuration.")
        return
    
    # 创建自定义区域（更安全的方式）
    zone_name = "cluster-zone"
    
    server.shell(
        name="Create Custom Firewall Zone",
        commands=[
            "systemctl restart firewalld",
            # 恢复默认
            f"firewall-cmd --permanent --delete-zone={zone_name} 2>/dev/null || true",
            # 创建新区域
            f"firewall-cmd --permanent --new-zone={zone_name}",
            # 设置默认策略为拒绝
            f"firewall-cmd --permanent --zone={zone_name} --set-target=DROP",
            # 允许SSH
            f"firewall-cmd --permanent --zone={zone_name} --add-service=ssh",
        ],
        # _sudo=True,
    )
    
    # 添加白名单IP到区域
    for ip in ip_white_list:
        if ip != pyinfra.host.name:
            print(f"---------- firewall allow ip: {ip} -----------")
            server.shell(
                name=f"Allow {ip} Access",
                commands=[
                    f"firewall-cmd --permanent --zone={zone_name} --add-rich-rule='rule family=\"ipv4\" source address=\"{ip}\" port port=\"9092\" protocol=\"tcp\" accept'",
                    f"firewall-cmd --permanent --zone={zone_name} --add-rich-rule='rule family=\"ipv4\" source address=\"{ip}\" port port=\"9093\" protocol=\"tcp\" accept'",
                ],
                _sudo=True,
            )
    
    # 将接口绑定到自定义区域
    server.shell(
        name="Bind Interface to Custom Zone",
        commands=[
            "firewall-cmd --permanent --zone=cluster-zone --change-interface=ens192 2>/dev/null || true",
            "firewall-cmd --reload",
            # 验证配置
            f"firewall-cmd --zone={zone_name} --list-all"
        ],
        # _sudo=True,
    )
    # sudo firewall-cmd --permanent --zone=cluster-zone --list-rich-rules
    