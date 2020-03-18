import os
import csv

FLAGS = None
_ = None


def get_onload(path):
    with open(path, 'r') as f:
        data = f.read().lower()
        if 'onload' in data:
            return True
        else:
            return False


def main():
    file_src = open(FLAGS.input, 'r')
    csv_src = csv.DictReader(file_src)

    # -----
    # fieldnames = csv_src.fieldnames + ['DataSize', 'onLoad']
    # if os.path.exists(path_dst):
    #     mode = 'a'
    # else:
    #     mode = 'w'
    # file_dst = open(path_dst, mode)
    # csv_dst = csv.DictWriter(file_dst, fieldnames=fieldnames)
    # if mode == 'w':
    #     csv_dst.writeheader()
    # -----
    fieldnames = csv_src.fieldnames + ['DataSize', 'onLoad']
    if os.path.exists(FLAGS.output):
        file_dst = open(FLAGS.output, 'a')
        csv_dst = csv.DictWriter(file_dst, fieldnames=fieldnames)
    else:
        file_dst = open(FLAGS.output, 'w')
        csv_dst = csv.DictWriter(file_dst, fieldnames=fieldnames)
        csv_dst.writeheader()

    cnt = 0
    for row_src in csv_src:
        row = row_src
        path = os.path.join(FLAGS.base, f'{row["ConvertedAddress"]}-{int(float(row["Time"]))}.html')
        row['DataSize'] = os.path.getsize(path)
        row['onLoad'] = get_onload(path)
        csv_dst.writerow(row)
        if cnt%10 == 0:
            print(f'Processed {cnt}', end='\r')
        cnt += 1
    print(f'Processed {cnt}')

    file_src.close()
    file_dst.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str,
                        default='./output/time.csv',
                        help='The addresses formed csv for testing')
    parser.add_argument('-o', '--output', type=str,
                        default='./output/output_1.csv',
                        help='The output directory for saving results')
    parser.add_argument('-b', '--base', type=str,
                        default='./output/html',
                        help='The html directory for reading')
    FLAGS, _ = parser.parse_known_args()

    # path preprocessing
    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    FLAGS.base = os.path.abspath(os.path.expanduser(FLAGS.base))

    main()
