import csv
import os
import re

def list_all_folders(path):
    '''list_all_folders
     args: oob path 파일이 있는 경로
     return: 파일 경로+oob path 파일리스트
    '''
    print(path)
    with os.scandir(path) as it:
      file_list = list()
      for entry in it:
        if entry.name.endswith('.tsv') and entry.is_file():
          yield path+entry.name


def get_onion_address(csv_file):
    onion_set = set()
    with open(csv_file) as csvfile:
      csv_reader = csv.reader(csvfile, delimiter='\t')
      for row in csv_reader:
        raw_onion = row[1]
        p = re.compile('https://[a-zA-Z0-9]+\.onion')
        m = p.match(raw_onion)
        if m:
          onion = m.group()
          onion_set.add(onion)
    return onion_set
        

def write_stack_txt(onion_address_set, path):
    all_set = set()

    if os.path.isfile(path):
      stored_set = read_onion_address(path)
      all_set = onion_address_set.union(stored_set)
    else:
      all_set = all_set.union(onion_address_set)

    all_list = list(all_set)
    with open(path, 'w') as csv_file:
      csv_writer = csv.writer(csv_file, delimiter=',')
      for onion_address in all_list:
        csv_writer.writerow(onion_address)


def read_onion_address(path):
    with open(path, 'r') as csv_file:                                           
      csv_reader = csv.reader(csv_file, delimiter=',')                          
      for row in csv_reader:                                                    
        stored_set.add(row[0])
    return stored_set

def divide_by_machine(onion_address_set, loc):
    print(onion_address_set)

    pass


def main(args):
    '''
    1. 모든폴더를 읽어들인다
    2. csv로부터 onion 주소 리스트만 뽑아낸다
    3. 중복검사를 한다(set()으로)
    4. machine에 중복검사해야한다.
    5. machine에분리해놓는다 
    '''
    onion_address_set = set()
    for csv_file in list_all_folders(args.input_file):
      file_result = get_onion_address(csv_file)
      onion_address_set = onion_address_set.union(file_result)
    write_stack_txt(onion_address_set, path)
    divide_by_machine(onion_address_set, args.machine_loc)
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='python parser')
    parser.add_argument('--input-file', '-i',
                        required=True,
                        help='oob address set')
    parser.add_argument('--onion-file,' '-o',
                        required=True,
                        help='input onion address')
    parser.add_argument('--machine-loc', '-m',
                        required=True,
                        help='input machine location')
    args = parser.parse_args()
    main(args)

