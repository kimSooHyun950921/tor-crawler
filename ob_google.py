import os
import json

from googleapiclient.discovery import build
import yaml

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
            for item in res['items']:
                print(item['link'])
            if 'nextPage' in res['queries']:
                start = res['queries']['nextPage'][0]['startIndex']
            else:
                break
            cnt += 1


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

