import os
import csv
import time

from tbselenium.tbdriver import TorBrowserDriver
from selenium.common.exceptions import WebDriverException as WebDriverException


addrpath = os.path.abspath(os.path.expanduser('./test_address.csv'))
opath = os.path.abspath(os.path.expanduser('./gui_output'))
mpath = os.path.abspath(os.path.expanduser('./gui.csv'))
driverpath = os.path.abspath(os.path.expanduser('/home/harny/.local/share/tor-browser_en-US'))

os.makedirs(opath, exist_ok=True)

driver = TorBrowserDriver(driverpath)


def get_address(path):
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row['Name'], row['Address']

mf = open(mpath, 'w')
writer = csv.writer(mf)

for name, addr in get_address(addrpath):
    ss = time.time()
    driver.get(addr)
    data = driver.page_source
    ofile = os.path.join(opath, f'{name}.html')
    with open(ofile, 'w') as f:
        f.write(data)
    ee = time.time()
    writer.writerow([name, addr, ee-ss])
    print(f'Done {name}')

mf.close()
driver.close()
