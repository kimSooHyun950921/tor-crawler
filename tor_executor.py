import crawler
import json
import subprocess
import time
def read_tor_path():
    with open("./TOR_PATH.json", 'r') as f:
        raw_file = f.read()
        raw_file.replace("\\","")
        return json.loads (raw_file)

def main():
    tor = read_tor_path()
    tor_path = tor["tor"]
    browser_path = tor["browser"]
    #토르 실행
    print("Executing Tor ...")
    subprocess.Popen(tor_path)

    time.sleep(10)
    #토르 크롤러 실행
    print("Excuting Tor Crawler ...")

    subprocess.run(["python3", "crawler.py",
                    "-d", browser_path])

if __name__ == '__main__':
    main()
