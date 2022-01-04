import os
import argparse
import requests
import hashlib
import pandas as pd
import AdRemover # python FIle "AdRemover"
import lxml
from lxml.html import tostring


def receive_adblock_rule():
    rule_urls = ["https://easylist-downloads.adblockplus.org/ruadlist+easylist.txt"]
    rule_files = [url.rpartition("/")[-1] for url in rule_urls]

    for rule_url, rule_file in zip(rule_urls, rule_files):
        r = requests.get(rule_url)
        with open(rule_file, "w") as f:
            print(r.text, file=f)


def remove_ads(data):

    remover = AdRemover("ruadlist+easylist.txt")
    document = lxml.html.document_fromstring(data)

    remover.remove_ads(document)
    clean_html = tostring(document).decode("utf-8")

    return clean_html

def create_integrity(data):

    data = str(data)
    data = data.strip()
    data = data.replace(" ", "")

    return hashlib.sha256(
        data.encode("utf-8")
    ).hexdigest()  # html 문자열 -> Byte로 변경(encode utf-8) -> sha256으로 해싱


def main():

    receive_adblock_rule()

    filename_list = os.listdir(FLAGS.input)

    os.makedirs('./output/cleanhtml', exist_ok = True)

    hashvalue_list = []

    for htmlfile_name in filename_list:
        with open(FLAGS.input + "/" + htmlfile_name, 'r') as d:
            htmlFile = d.read()
        clean_ads_htmlfile = remove_ads(htmlFile)
        clean_ads_htmlfile_hashvalue = create_integrity(clean_ads_htmlfile)

        hashvalue_list.append([htmlfile_name, clean_ads_htmlfile_hashvalue])
        
        
        with open(FLAGS.output + "/" + htmlfile_name, "w") as f:
            print(clean_ads_htmlfile, file = f)
    
    hashvalue_df= pd.DataFrame(hashvalue_list)
    hashvalue_df.columns = ['FileName', 'hash']
    hashvalue_df.to_csv('HashValueHtmlFile.csv', index = False)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="./output/html/",
        help="HTML file Folder for remove Ads",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./output/cleanhtml/",
        help="The output directory for saving results",
    )
    FLAGS, _ = parser.parse_known_args()

    # path preprocessing
    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
