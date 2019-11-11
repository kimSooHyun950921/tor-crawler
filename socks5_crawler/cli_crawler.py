import os
import csv

import time
import requests

addrpath = os.path.abspath(os.path.expanduser('./test_address.csv'))
opath = os.path.abspath(os.path.expanduser('./cli_output'))
mpath = os.path.abspath(os.path.expanduser('./cli.csv'))

os.makedirs(opath, exist_ok=True)

session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9050'
session.proxies['https'] = 'socks5h://localhost:9050'



def get_address(path):
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row['Name'], row['Address']

mf = open(mpath, 'w')
writer = csv.writer(mf)

for name, addr in get_address(addrpath):
    ss = time.time()
    data = session.get(addr).text
    ofile = os.path.join(opath, f'{name}.html')
    with open(ofile, 'w') as f:
        f.write(data)
    ee = time.time()
    writer.writerow([name, addr, ee-ss])
    print(f'Done {name}')

mf.close()

