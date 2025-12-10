from pyinfra import host
from pyinfra.operations import files, server


# 从 host 变量中获取 ip_white_list 列表
ip_white_list: list = host.group_data.get("ip_white_list", [])


# print("xxxxxxxxxxxx ", ip_white_list)
# print('xxxxxxxxxxxxxxxxxxxx ', host.data.dict())

# 新建 elasticsearch 运行用户和组: elastic
def elastic_user():
    es_user = host.data.get('es_user', 'elastic')
    es_group = host.data.get('es_group', 'elastic')
    server.group(
        name=f"Add User: {es_user}",
        group=es_group,
        system=True,
        # _sudo=True,
    )
    server.user(
        name=f"Add Group: {es_group}",
        user=es_user,
        system=True,
        create_home=False,
        group=es_group,
        _sudo=True,
    )


# 关闭节点交换分区
def swap():
    files.line(
        name="Disable Swap",
        path="/etc/fstab",
        line="swap",
        replace="^.*swap.*$",
        present=False,
        backup=True,
        #  _sudo=True,
    )


# 关闭selinux
def selinux():
    files.line(
        name="Disable SELinux",
        path="/etc/selinux/config",
        line="SELINUX=disabled",
        replace="^SELINUX=.*$",
        backup=True,
        #  _sudo=True,
    )


# 配置节点 ulimit 限制
def ulimit():
    files.template(
        name="Setup Ulimit",
        src="templates/limits.conf.j2",
        dest="/etc/security/limits.conf",
        mode="644",
        backup=True,
        #  _sudo=True,
    )


# 配置节点内核参数
def sysctl():
    files.template(
        name="Setup Sysctl",
        src="templates/99-sysctl.conf.j2",
        dest="/etc/sysctl.d/99-sysctl.conf",
        mode="644",
        backup=True,
        # _sudo=True,
    )
    server.shell(
        name="Apply Sysctl Settings",
        commands=["sysctl --system"],
        # _sudo=True,
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


# 配置各个节点防火墙规则
# 让各个节点可以通过ip白名单相互通信
def firewalld():
    if not ip_white_list:
        print("ip_white_list 为空，跳过防火墙配置")
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
        if ip != host.name:
            print(f"---------- firewall allow ip: {ip} -----------")
            server.shell(
                name=f"Allow {ip} Access",
                commands=[
                    f"firewall-cmd --permanent --zone={zone_name} --add-rich-rule='rule family=\"ipv4\" source address=\"{ip}\" port port=\"9200\" protocol=\"tcp\" accept'",
                    f"firewall-cmd --permanent --zone={zone_name} --add-rich-rule='rule family=\"ipv4\" source address=\"{ip}\" port port=\"9300\" protocol=\"tcp\" accept'",
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

    
# 安装必要命令工具
def tools():
    # dnf.packages(
    #     name="安装必要命令工具",
    #     packages=[
    #         "tar.x86_64"
    #     ],
    #     update=True,
    #     _sudo=True,
    # )
    server.shell(
        name="Install Necessary Tools",
        commands=["dnf install -y tar.x86_64 unzip.x86_64"],
        # _sudo=True,
    )

# 安装 openjdk
def openjdk():
    # 上传jdk包
    openjdk_package = host.data.get('jdk_package', 'openjdk-8u321-linux-x64.tar.gz')
    files.put(
        f"files/{openjdk_package}",
        f"/tmp/{openjdk_package}",
        # _sudo=True,
    )
    # 解压 JDK 包
    server.shell(
        name="Extract JDK Package",
        commands=[f"tar -zxvf /tmp/{openjdk_package} -C /usr/local/"],
        _sudo=True,
    )
    # 配置 JDK 环境变量
    files.template(
        name="Configure JDK Environment Variables",
        src="templates/java.sh.j2",
        dest="/etc/profile.d/java.sh",
        mode="644",
        # _sudo=True,
    )