import os
import csv
import re
import datetime

from onion_address import extract_address

FLAGS = None
_ = None
FIELDNAMES = ['Name', 'Address', 'Timestamp']


def get_timestamp(date):
    tz_seoul = datetime.timezone(datetime.timedelta(hours=9))
    tz_utc = datetime.timezone(datetime.timedelta())

    d = datetime.datetime.strptime(date, '%y%m%d')
    d = d.replace(tzinfo=tz_seoul)

    return d.timestamp()


def main():
    file_dst = open(FLAGS.output, 'w')
    csv_dst = csv.DictWriter(file_dst, fieldnames=FIELDNAMES,
                             quoting=csv.QUOTE_MINIMAL,
                             lineterminator=os.linesep)
    csv_dst.writeheader()

    known = set()
    with os.scandir(FLAGS.input) as it:
        for entry in it:
            if entry.is_file():
                file_src = open(entry.path, 'r')
                tsv_src = csv.DictReader(file_src,
                                         fieldnames=['Title', 'Link', 'Date'],
                                         delimiter='\t')
                for row in tsv_src:
                    address = extract_address(row['Link'], True)
                    if len(address) == 0:
                        continue
                    elif address in known:
                        continue
                    title = row['Title']
                    timestamp = get_timestamp(row['Date'])

                    known.add(address)
                    csv_dst.writerow({'Name': title,
                                      'Address': address,
                                      'Timestamp': timestamp})

    file_dst.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='The legacy addresses')
    parser.add_argument('-o', '--output', type=str,
                        default='./legacy_address.csv',
                        help='The output file for saving results')
    FLAGS, _ = parser.parse_known_args()

    # path preprocessing
    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
