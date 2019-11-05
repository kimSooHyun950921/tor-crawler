from time import strftime, localtime, time, sleep 
from  datetime import datetime
import csv
import os
import subprocess 
import traceback
from pyvirtualdisplay import Display

import requests
from selenium.common.exceptions import TimeoutException as SelTimeExcept
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions \
import NoSuchWindowException as SelWindowExcept
from selenium.common.exceptions \
import WebDriverException as SelWebDriverExcept


from tbselenium.tbdriver import TorBrowserDriver
from tor_pageCrawler_enum import RequestsErrorCode as torReqEnum
from tor_pageCrawler_enum import tbSeleniumErrorCode as torSelEnum


OUTPUT_PATH = dict()
INPUT_PATH = dict()

ACCESS_TIMEOUT = 120                                                            
MAX_TAB_NUM = 5                                                                 
MAX_QUEUE_NUM = 2                                                               
                                                                                
DEFAULT_XVFB_WIN_W = 1280                                                       
DEFAULT_XVFB_WIN_H = 800                                                        
XVFB_DISPLAY = Display(visible=0, \
                       size=(DEFAULT_XVFB_WIN_W, 
                       DEFAULT_XVFB_WIN_H))                                  
digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'  

def make_input_dir(path):
   '''make_input_dir: input 디렉터리 정리
   args: Root Director
   return: None:
   Input directory 종류:
   1. TBB path
   2. oion주소'''
   input_path = path + 'INPUT/'
   INPUT_PATH["TBB_PATH"] = input_path + 'TBB/'
   INPUT_PATH["ONION_PATH"] = input_path + 'ONION_LINK/'
   return INPUT_PATH


def make_output_dir(path):
   '''make_output_dir: 결과물을 위한 output디렉터리 정리
   args: Root Directory
   return: None
   1. Root Directory로부터
   2. (없다면)첫번째 깊이 디렉터리 만들기(output, log)
   3. output 디렉터리 만들기(ls_live, html, header, page info)
   '''
   out_path = make_dirs(path+'OUTPUT/')

   OUTPUT_PATH["LOG_PATH"] = make_dirs(path+'LOG/')
   OUTPUT_PATH["SEVER_PATH"] = make_dirs(out_path+'SERVER_LIVE_SET/')#이름바꾸기
   OUTPUT_PATH["HTML_PATH"] = make_dirs(out_path+'HTML_SET/')
   OUTPUT_PATH["LOG_PATH"] = make_dirs(out_path+'LOG_SET/')
   OUTPUT_PATH["HEADER_PATH"] = make_dirs(out_path+'HEADER_SET/')
  # OUTPUT_PATH[""] = make_dirs(out_path+'PAGE_INFO_SET/')#TODO 뭔지 모르겠다..


def make_path_dir(path):
  INPUT_PATH = make_input_dir(path)
  OUTPUT_PATH = make_output_dir(path)


def make_dirs(dir_path):
   if not os.path.exists(dir_path):
      os.makedirs(dir_path)
   return dir_path

   
def cur_date():
 curdate = datetime.today().strftime("%Y-%m-%d")
 return curdate


def open_tor_browser():
   open_tor_browser = False
   try_count = 0
   driver = None

   while not open_tor_browser and try_count < 5:
     try:
       try_count += 1
       driver = TorBrowserDriver(INPUT_PATH["TBB_PATH"],\
                                 tbb_logfile_path='./tor_browser_log.txt')
       open_tor_browser = True
       print(driver)
     except SelWebDriverExcept as e:
       print(e)
       print("[BROWSER_ERROR] Tor Browser Open Error! Try Reopening...")
       continue
       return driver


def read_input():
   all_csv_file = os.listdir(INPUT_PATH['ONION_PATH'])
   reader_list = list()

   for csv_file in all_csv_file:
     read_file = open(INPUT_PATH['ONION_PATH']+csv_file, 'r')
     reader = csv.reader(read_file, delimiter='\t')
     for row in reader:
       reader_list.append(row)
   return reader_list
   

def request_setup():
   session = requests.Session()
   session.proxies = {'http': 'socks5h://localhost:9050',\
                      'https': 'socks5h://localhost:9050'}
   session.headers = {'User-Agent':\
   'Mozilla/5.0(Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0'}
   return session


def crawler_logging(mode, log):
    file_name = cur_date() + ".txt"
    crawler_logger = open(OUTPUT_PATH['LOG_PATH']+"/"+file_name, mode)
    crawler_logger.write(log)
    crawler_logger.close()


def hs_main_page_get(driver, onion_address):
    try:
      driver.load_url(onion_address,\
                      wait_on_page=ACCSS_TIMEOUT,\
                      wait_for_page_body=True)
    except SelWebDriverExcept:
      return torSeleEnum.TB_SEL_WEBDRIVER_EXCEPT.value
    except SelTimeExcept:
      return torSelenim.TB_SEL_TIME_EXCEPT.value
    except:
      e_log = traceback.format_exc()
      crawler_logging("a", "[TB_SEL_UNDEFINED_EXCEPT] : "+\
                      strftime("%Y/%m/%d-%H%M:%S", localtime(time()))+\
                      "\nin"+ onion_address + "\n" + e_log)
      return torSelEnum.TB_SEL_UNDEFINED_EXCEPT.value
    return torSelEnum.TB_SEL_SUCCESSS.value


def tor_crawling(session, reader_list, driver):
   '''tor_crawling: 크롤링
   args : 크롤러 리스트, driver
   return : None
   '''
   address_queue = list()
   for reader in reader_list:
     print(reader)
     onion_address = reader[0]
     hs_main_page_get(driver, onion_address)
     status_code = hs_request_status_code(session, onion_address)
     write_status_code(status_code)
     

def write_status_code(status_code):
  address_queue = list()
  if status_code < 400 or status_code == tor.ReqEnum.REQ_UNDEFINED_EXCEPT.value:
     address_queue.append(row)
  elif status_code != (404 or 410) and status_code < 500:
     row.append(cur_date(True))
     row.append("live")
     row.append(str(status_code))
  elif status_code == torReqEnum.REQ_CONNECT_TIMER.value:
     row.append(cur_date(True))
     row.append("dead")
     row.append("REQ_connectionTimeout")
     row.append("write dead")
  elif status_code == torReqEnum.REQ_READ_TIMEOUT.value:
     row.append(cur_data(True))
     row.append("dead")
     row.append("REQ_readTimeout")
     write_output_file(row)
     print("write dead")
  elif status_code == torReqEnum.REQ_CONNCTIon_ERROR.value:
     row.append(cur_date(True))
     row.append("dead")
     row.append("REQ_connectionError")
     #write.writerow(row)
     print("write dead")
  else:
     row.append(cur_date(True))
     row.append("dead")
     row.append(hs_status_code)
     write_output_file(row)


def write_output_file(row):
    print(row)


def write_header_list(header):
  file_name = 'hidden_service_header.csv'
  with open(OUTPUT_PATH['HEADER_PATH']+file_name, 'a') as hs_header_list_file:
   hs_header_list_file.write(header)
    


def hs_request_status_code(session, onion_address):
   try:
     response = session.get(onion_address, timeout=ACCESS_TIMEOUT)
     hs_status_code = response.status_code
     hs_header = str(response.headers)
     write_header_list(onion_address+'\t'+hs_header+'\n')
   except requests.ConnectTimeout:
     return torReqEnum.REQ_CONNECT_TIMEOUT.value
   except requests.ReadTimeout:
     return torReqEnum.REQ_READ_TIMEOUT.value
   except requests.ConnectionError:
     return torReqEnum.REQ_CONNECTION_ERROR.value
   except Exception as e:
     print(e)
     return torReqEnum.REQ_UNDEFINDED_EXCEPT.value
   return hs_status_code


def main(path, timeout):
 # 준비
 # TODO PATH 만들기 => 완료
 make_path_dir(path)
 # TODO TOR Browser 열기=> 완료
 driver = open_tor_browser() 
 # TODO session열기 => 완료
 session = request_setup()
 print("SESSION:", session)

 # 읽기
 # TODO 읽어야할 파일 가져오기==> 완료
 reader_list = read_input()

 # 처리
 # TODO 크롤링하기
 tor_crawling(session, reader_list, driver)


if __name__ == "__main__":
  #TODO ARG parse로 root directory 가져오기(여기엔 INPUT도 있어야함)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--rootdirectory", "-d", 
                      help = "root directory")
  parser.add_argument("--timeout", "-t",
                      help = "timeout")
  args = parser.parse_args()
  #TODO 찾아봐야할것 : rootdirectory
  main(args.rootdirectory, args.timeout)
