

import subprocess




dns_resolvers = [
    '8.8.8.8',
    '9.9.9.9',
    '208.67.222.222',
    '1.1.1.1',
    '185.228.168.9',
    '76.76.19.19',
    '94.140.14.14',
    '84.200.69.80',
    '8.26.56.26',
    '205.171.3.65',
    '195.46.39.39',
    '159.89.120.99',
    '216.146.35.35',
    '77.88.8.8',
    '74.82.42.42',
    '64.6.64.6',
    '76.76.2.0'
]



def init():
    resolvers = dns_resolvers
    for resolver in resolvers:
        try:
            command = "resperf-report  -s {} -d querytxt".format(resolver)
            subprocess.Popen(command.split()).wait()
        except:
            continue

init()