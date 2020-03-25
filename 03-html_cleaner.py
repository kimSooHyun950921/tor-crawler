import os
import csv

from send2trash import send2trash

FLAGS = None
_ = None


def main():
    file_src = open(FLAGS.input, 'r')
    csv_src = csv.DictReader(file_src)

    listed = set()
    for row_src in csv_src:
        row = row_src
        path = os.path.join(FLAGS.base, f'{row["ConvertedAddress"]}-{int(float(row["Time"]))}.html')
        if path in listed:
            print(f'Duplicated! {row_src}')
        listed.add(path)
    print(f'Listed: {len(listed)}')

    downloaded = set()
    with os.scandir(FLAGS.base) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                downloaded.add(entry.path)
    print(f'Downloaded: {len(downloaded)}')

    prune = downloaded.difference(listed)
    print(f'Delete: {len(prune)}')
    for path in prune:
        send2trash(path)

    file_src.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str,
                        default='./output/time.csv',
                        help='The addresses formed csv for testing')
    parser.add_argument('-b', '--base', type=str,
                        default='./output/html',
                        help='The html directory for reading')
    FLAGS, _ = parser.parse_known_args()

    # path preprocessing
    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.base = os.path.abspath(os.path.expanduser(FLAGS.base))

    main()
