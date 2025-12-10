
# 三节点, es_node与group_data中文件名需保持一致
# es_node 组内的每个主机可以有自己的变量
es_node = [
    ('192.168.165.83', {'elastic_node_name': 'es-node-1'}),
    ('192.168.165.84', {'elastic_node_name': 'es-node-2'}),
    ('192.168.165.85', {'elastic_node_name': 'es-node-3'})
]

# kb_node
kb_node = [  
    ('192.168.165.87', {}),
]