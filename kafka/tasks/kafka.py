import pyinfra
from pyinfra.operations import server, files, systemd


@pyinfra.api.deploy('Run Kafka Deployment')
def run():
    user = pyinfra.host.data.get('kafka_user', 'kafka')
    group = pyinfra.host.data.get('kafka_group', 'kafka')
    kafka_install_path = pyinfra.host.data.get('kfk_install_path', '/usr/local')
    kafka_package_name = pyinfra.host.data.get('kfk_package_name', 'kafka_2.13-4.1.1.tgz')
    kafka_work_path = pyinfra.host.data.get('kfk_work_path')
    kafka_data_path = pyinfra.host.data.get('kfk_data_path', '/var/lib/kafka')
    # 上传 kafka 包
    files.put(
        name="Upload Kafka Package",
        src=f"files/{kafka_package_name}",
        dest=f"/tmp/{kafka_package_name}",
        mode='0644',
    )

    # 解压 kafka 包
    server.shell(
        name="Extract Kafka Package",
        commands=[
            f"tar -xzf /tmp/{kafka_package_name} -C {kafka_install_path}",
            f"chown -R {user}:{group} {kafka_work_path}",
        ]
    )

    # 上传 配置文件
    files.template(
        name="Upload Kafka Config Files",
        src="templates/server.properties.j2",
        dest=f"{kafka_work_path}/config/server.properties",
        mode='0644',

    )

    # 格式化存储目录
    files.template(
        name="Upload Kafka Storage Format Script",
        src="templates/random-uuid.sh.j2",
        dest=f"{kafka_work_path}/bin/random-uuid.sh",
        mode='0755',
    )
    server.shell(
        name="Format Kafka Storage Directory",
        commands=[
            f"sudo -u {user} {kafka_work_path}/bin/random-uuid.sh",
        ]
    )

    # 修改 kafka 工作目录权限
    server.shell(
        name="Set Kafka Work Path Permissions",
        commands=[
            f"chown -R {user}:{group} {kafka_work_path} {kafka_data_path}",
        ]
    )

    # 启动 kafka 服务
    files.template(
        name="Upload Kafka Systemd Service File",
        src="templates/kafka.service.j2",
        dest="/etc/systemd/system/kafka.service",
        mode='0644',
    )
    systemd.service(
        name="Enable and Start Kafka Service",
        service="kafka",
        enabled=True,
        running=True,
        daemon_reload=True,
    )