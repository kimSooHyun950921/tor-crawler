import os
import sys
import csv
import time
import hashlib
import multiprocessing


import requests
import psutil

FIELD_TIME = ['Type', 'Time', 'Name', 'Address', 'ConvertedAddress',
              'ResponseTime']
FLAGS = None
_ = None


def check_process(psname='tor'):
    for proc in psutil.process_iter():
        if proc.name() == psname:
            return True
    return False


def get_address(path):
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def get_session():
    session = requests.session()
    session.proxies = {}
    session.proxies['http'] = f'socks5h://localhost:{FLAGS.port}'
    session.proxies['https'] = f'socks5h://localhost:{FLAGS.port}'
    session.headers['User-Agent'] = 'Mozilla/5.0'
    return session


def convert_addr(value):
    return hashlib.md5(value.encode('utf-8')).hexdigest()


def do_crawl(args):
    global FLAGS

    name = args['Name']
    addr = args['Address']
    session = get_session()

    time_start = time.time()
    try:
        data = session.get(addr).text
    except requests.exceptions.ConnectionError:
        data = ''
    conv_addr = convert_addr(addr)
    path_html = os.path.join(FLAGS.output, 'html',
                             f'{conv_addr}-{int(time_start)}.html')
    with open(path_html, 'w') as f:
        f.write(data)
    time_end = time.time()
    
    print(f'[{os.getpid()}] {name:^20.20s} {addr:^50.50s}')

    return {'Type': 'CLI',
            'Time': time_start,
            'Name': name,
            'Address': addr,
            'ConvertedAddress': conv_addr,
            'ResponseTime': time_end - time_start}


def main():
    print(f'Parsed arguments: {FLAGS}')
    print(f'Unparsed arguments: {_}')

    if not check_process():
        print('Need to running tor for socks5')
        sys.exit(0)

    print('Start up crawler')
    # prepare job
    os.makedirs(FLAGS.output, exist_ok=True)
    os.makedirs(os.path.join(FLAGS.output, 'html'), exist_ok=True)
    path_time = os.path.join(FLAGS.output, 'time.csv')
    if os.path.exists(path_time):
        file_time = open(path_time, 'a')
        writer_time = csv.DictWriter(file_time, fieldnames=FIELD_TIME,
                                     quoting=csv.QUOTE_MINIMAL,
                                     lineterminator=os.linesep)
    else:
        file_time = open(path_time, 'w')
        writer_time = csv.DictWriter(file_time, fieldnames=FIELD_TIME,
                                     quoting=csv.QUOTE_MINIMAL,
                                     lineterminator=os.linesep)
        writer_time.writeheader()

    time_start = time.time()
    with multiprocessing.Pool(FLAGS.number) as p:
        joined_rows = p.imap(do_crawl, get_address(FLAGS.input))

        for row in joined_rows:
            writer_time.writerow(row)
    time_end = time.time()

    file_time.close()
    print(f'End up crawler after {time_end - time_start}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='The addresses formed csv for testing')
    parser.add_argument('-o', '--output', type=str,
                        default='./output',
                        help='The output directory for saving results')
    parser.add_argument('-p', '--port', type=int,
                        default=9050,
                        help='The port number of Tor socks5h server')
    parser.add_argument('-n', '--number', type=int,
                        default=8,
                        help='The number of process pool')
    FLAGS, _ = parser.parse_known_args()

    # path preprocessing
    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
