"""
组变量定义文件
这里的变量会被所有属于 kb_node 组的主机共享
kb_node 组定义在 inventories/inventory.py 文件中
"""

## kibana 节点
kb_node_ips = [
    '192.168.165.87',
]


## es 节点主机地址列表
es_hosts = [
    "https://192.168.165.83:9200",
    "https://192.168.165.84:9200",
    "https://192.168.165.85:9200",
]