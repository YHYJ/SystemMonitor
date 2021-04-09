{
    'timestamp': '2021-04-09 15:52:06',
    'deviceid': 'Test',
    'devicename': 'Test-machine',
    'schema': 'public',
    'table': 'example',
    'fields': {
        'cpu': {
            'percent': 0.0
        },
        'memory': {
            'total': 15.5,
            'available': 12.4,
            'percent': 19.8,
            'used': 2.4,
            'free': 10.7,
            'active': 0.6,
            'inactive': 3.8,
            'buffers': 0.2,
            'cached': 2.2,
            'shared': 0.4,
            'slab': 0.2
        },
        'swap': {
            'total': 0.0,
            'used': 0.0,
            'free': 0.0,
            'percent': 0.0,
            'sin': 0.0,
            'sout': 0.0
        },
        'disk': {
            'total': 233.2,
            'used': 27.0,
            'free': 194.3,
            'percent': 12.2
        },
        'nic': [{
            'name': 'lo',
            'macaddr': '00:00:00:00:00:00',
            'ipaddr': '127.0.0.1',
            'netmask': '255.0.0.0'
        }, {
            'name': 'wlp3s0',
            'macaddr': '34:41:5d:83:07:2f',
            'ipaddr': '192.168.3.9',
            'netmask': '255.255.255.0'
        }],
        'mac': {
            'wan': '00:00:00:00:00:00',
            'lan': '34:41:5d:83:07:2f'
        },
        'process': [{
            'name': 'python',
            'keyword': 'monitor',
            'pid': 91523,
            'status': 'running',
            'running': 1
        }]
    }
}
