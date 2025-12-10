### kafka

- **软件包准备**
```bash
files/kafka_2.13-4.1.1.tgz
files/openjdk-17.0.2_linux-x64_bin.tar.gz
```

- **部署集群**
```bash
# 执行单条命令
# pyinfra inventories/inventory.py exec -- 'reboot'

pyinfra inventories/inventory.py deploy.py -y
pyinfra inventories/inventory.py deploy.py --data action=setup -y
pyinfra inventories/inventory.py deploy.py --data action=kafka -y
```