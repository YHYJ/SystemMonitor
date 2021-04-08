{
    'timestamp': '2021-04-08 10:25:05',
    'deviceid': 'Test',
    'devicename': 'Test-machine',
    'filename': 'system_monitor_data.txt',
    'mode': 'add',
    'fields': {
        'cpu': {
            'percent': 12.5
        },
        'memory': {
            'total': 15.5,
            'available': 13.4,
            'percent': 13.4,
            'used': 1.5,
            'free': 10.6,
            'active': 1.2,
            'inactive': 3.1,
            'buffers': 0.5,
            'cached': 3.0,
            'shared': 0.3,
            'slab': 0.3
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
            'used': 26.1,
            'free': 195.2,
            'percent': 11.8
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
        'process': [{
            'name': 'python',
            'keyword': 'main',
            'pid': 783982,
            'status': 'running',
            'running': 1
        }]
    }
}
