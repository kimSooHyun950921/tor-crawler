import os
import csv
import json
import time

from googleapiclient.discovery import build
import yaml

from onion_address import extract_address

# If it was modified, then need to sync crawler
FIELDNAMES = ['Name', 'Address', 'Timestamp']
FLAGS = None
_ = None
CFG = None


def load_config(cfg_path='config.yaml'):
    global CFG
    with open(cfg_path, 'r') as f:
        CFG = yaml.safe_load(f)


def get_cse():
    global CFG
    service = build('customsearch', 'v1',
                    developerKey=CFG['auth']['api_key'])
    return service.cse()


def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    # load configuration
    load_config(FLAGS.config)

    if os.path.exists(CFG['outofband']['output']):
        file_output = open(CFG['outofband']['output'], 'a')
        writer_output = csv.DictWriter(file_output, fieldnames=FIELDNAMES,
                                       quoting=csv.QUOTE_MINIMAL,
                                       lineterminator=os.linesep)
    else:
        file_output = open(CFG['outofband']['output'], 'w')
        writer_output = csv.DictWriter(file_output, fieldnames=FIELDNAMES,
                                       quoting=csv.QUOTE_MINIMAL,
                                       lineterminator=os.linesep)
        writer_output.writeheader()

    # get service
    cse = get_cse()

    # loop search keyword
    for keyword in CFG['search']['keywords']:
        cnt = 0
        start = None
        while cnt < CFG['search']['quota']//len(CFG['search']['keywords']):
            res = cse.list(q=keyword,
                           cx=CFG['auth']['id'],
                           start=start).execute()
            if 'items' not in res:
                break
            for item in res['items']:
                addr = extract_address(item['link'])
                if len(addr) == 0:
                    continue
                writer_output.writerow({'Name': item['title'],
                                        'Address': addr,
                                        'Timestamp': time.time()})
            cnt += 1
            if 'nextPage' in res['queries']:
                start = res['queries']['nextPage'][0]['startIndex']
            else:
                break
        print(f'Search done {cnt} page for {keyword}')

    # terminate
    file_output.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', type=str,
                        default='config.yaml',
                        help='The configuration file path')
    FLAGS, _ = parser.parse_known_args()

    # Preprocessing for some arguments
    FLAGS.config = os.path.abspath(os.path.expanduser(FLAGS.config))

    # Excute main
    main()
