### elastc

* **证书和包准备**
```bash
# 解压 es 软件包后生成
files/ca.zip
files/client.zip

### elasticsearch 目录下执行
# bin/elasticsearch-certutil ca --pem --out config/certs/ca.zip
# unzip config/certs/ca.zip -d config/certs/
# bin/elasticsearch-certutil cert --ca-cert config/certs/ca/ca.crt --ca-key config/certs/ca/ca.key --name client --pem --out config/certs/client.zip
# cp config/certs/{ca.zip,client.zip} files/

# 下载 es kibana jdk 软件包
files/elasticsearch-9.1.1-linux-x86_64.tar.gz
files/kibana-9.1.1-linux-x86_64.tar.gz
files/openjdk-17.0.2_linux-x64_bin.tar.gz

files/ca.zip
```

* **部署集群**
    + 部署es: pyinfra inventories/inventory.py deploy.py --data es=true --parallel 3 -y
    + 创建用户配置templates/kibana.yml.j2中的用户密码: bin/elasticsearch-setup-passwords auto
    + 部署kb: pyinfra inventories/inventory.py deploy.py --data kb=true --parallel 3 -y

* **创建用户**
```bash
# ES节点上执行, 记录输出
bin/elasticsearch-setup-passwords auto
# ******************************************************************************
# Note: The 'elasticsearch-setup-passwords' tool has been deprecated. This       command will be removed in a future release.
# ******************************************************************************

# Initiating the setup of passwords for reserved users elastic,apm_system,kibana,kibana_system,logstash_system,beats_system,remote_monitoring_user.
# The passwords will be randomly generated and printed to the console.
# Please confirm that you would like to continue [y/N]y


# Changed password for user apm_system
# PASSWORD apm_system = ODs574DzHb0fgKuvsaeX

# Changed password for user kibana_system
# PASSWORD kibana_system = sHQUXhQS7VgqKCKErPJZ

# Changed password for user kibana
# PASSWORD kibana = sHQUXhQS7VgqKCKErPJZ

# Changed password for user logstash_system
# PASSWORD logstash_system = LOpZ6BeynUaZTmBejjkp

# Changed password for user beats_system
# PASSWORD beats_system = ZMmYpKet8ZrlCxZElwJr

# Changed password for user remote_monitoring_user
# PASSWORD remote_monitoring_user = gYdrAAxtmHLq3GTmEKhE

# Changed password for user elastic
# PASSWORD elastic = itmm7C3AfQYIcfk5vm2v
```

* **集群状态检查**
```bash
# es节点上执行
curl -u elastic:RpXIqhQk3LF7wnFX0BYk 'https://${EsNodeIp}:9200/_cluster/health?pretty' -k config/certs/ca/ca.crt
```
