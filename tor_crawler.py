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

import codecs

OUTPUT_PATH = dict()
INPUT_PATH = dict()

ACCESS_TIMEOUT = 120                                                            
MAX_TAB_NUM = 5                                                                 
MAX_QUEUE_NUM = 1                                                         
                                                                                
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
   INPUT_PATH["TBB_PATH"] = input_path + 'TBB/tor-browser_en-US'
   INPUT_PATH["ONION_PATH"] = input_path + 'ONION_LINK/machine_1/'#onion_link_set1.tsv'


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
   OUTPUT_PATH["SERVER_LIVE_PATH"] = make_dirs(out_path+'SERVER_LIVE_SET/')#이름바꾸기
   OUTPUT_PATH["HTML_PATH"] = make_dirs(out_path+'HTML_SET/')
   OUTPUT_PATH["LOG_PATH"] = make_dirs(out_path+'LOG_SET/')
   OUTPUT_PATH["HEADER_PATH"] = make_dirs(out_path+'HEADER_SET/')


   OUTPUT_PATH["LOG_PATH"] = OUTPUT_PATH["LOG_PATH"]
   OUTPUT_PATH["SERVER_LIVE_PATH"] = OUTPUT_PATH["SERVER_LIVE_PATH"] + \
                                     "output_1_"+cur_date()+".tsv"
   OUTPUT_PATH["HTML_PATH"] = OUTPUT_PATH["HTML_PATH"] + "html_source_dir_"+\
                                                          cur_date()
   OUTPUT_PATH["HEADER_PATH"] = OUTPUT_PATH["HEADER_PATH"] +\
                                "hidden_service_header1.tsv"

                                      
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
#     try:
       try_count += 1
       driver = TorBrowserDriver(INPUT_PATH["TBB_PATH"],\
                                 tbb_logfile_path='./tor_browser_log.txt')
       open_tor_browser = True
       print("[DRIVER OPEN SUCESS]",driver)
#     except SelWebDriverExcept as e:
#       print(e)
#       print("[BROWSER_ERROR] Tor Browser Open Error! Try Reopening...")
#       continue
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
    print("hs_main_page_get")
    status_code = torSelEnum.TB_SEL_SUCCESS.value
    try:
      driver.load_url(onion_address,\
                      wait_on_page=ACCESS_TIMEOUT,\
                      wait_for_page_body=True)
      print("wait_for_page_body") 
    except SelWebDriverExcept as e:
      print("SelWebDriverException", e)
      status_code = torSelEnum.TB_SEL_WEBDRIVER_EXCEPT.value
      return status_code
    except SelTimeExcept as e:
      print("SelTimeExcept", e)
      status_code = torSelEnum.TB_SEL_TIME_EXCEPT.value
      return status_code
    except Exception as e:
      print("ERROR:", e)
      e_log = traceback.format_exec()
      crawler_logging("a", "[TB_SEL_UNDEFINED_EXCEPT] : "+\
                      strftime("%Y/%m/%d-%H%M:%S", localtime(time()))+\
                      "\nin"+ onion_address + "\n" + e_log)
      status_code = torSelEnum.TB_SEL_UNDEFINED_EXCEPT.value
      return status_code
    print("Return Correct")
    return status_code
     

def write_status_code(status_code, row):
    address_queue = list()
    print("status_code:", status_code, "tor_ReqEnum:", torReqEnum.REQ_UNDEFINED_EXCEPT.value)
    if status_code < 400 or status_code == torReqEnum.REQ_UNDEFINED_EXCEPT.value:
       return 'a', row
    elif status_code != (404 or 410) and status_code < 500:
       row_list = [cur_date(), "live", str(status_code)]
       return 'w', row_list
    elif status_code == torReqEnum.REQ_CONNECT_TIMEOUT.value:
       row_list = [cur_date(), "dead", "REQ_connectionTimeout", "write_dead"]
       return 'w', row_list
    elif status_code == torReqEnum.REQ_READ_TIMEOUT.value:
       row_list = [cur_date(), "dead", "REQ_readTimeout"]
       return 'w', row_list
    elif status_code == torReqEnum.REQ_CONNECTION_ERROR.value:
       row_list = [cur_date(), "dead", "REQ_connectionError"]
       return 'w', row_list
    else:
       row_list = [cur_date(), "dead", hs_status_code]
       return 'w', row_list


def write_output_file(row):
    with open(OUTPUT_PATH["SERVER_LIVE_PATH"], 'a') as output_file:
      writer = csv.writer(output_file, delimiter='\t')
      writer.writerow(row)


def write_header_list(header):
  file_name = 'hidden_service_header.csv'
  with open(OUTPUT_PATH['HEADER_PATH']+file_name, 'a') as hs_header_list_file:
   hs_header_list_file.write(header)
    

def hs_request_status_code(session, onion_address):
   print("hs_request_status_code")
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
   print(hs_status_code)
   return hs_status_code


def tor_crawling(address_queue, driver,idx,leng):
    print("ADDRESS LENGTH: ", len(address_queue))
    print("MAX_QUEUE_NUM: ", MAX_QUEUE_NUM)
    if len(address_queue) == MAX_QUEUE_NUM or idx == leng-1:
      print("QUEUE IS MAX")
      tab_list = open_tab(address_queue, driver)
      crawl_tab(tab_list, driver)
      reset_other_tabs(driver)

    
def reset_other_tabs(driver):                                                   
    other_tab_idx = driver.window_handles                                       
    while len(other_tab_idx) > 1:                                               
        for tab_idx_num in range(1,len(other_tab_idx)):                         
            driver.switch_to_window(other_tab_idx[tab_idx_num])                 
            driver.close()                                                      
        other_tab_idx = driver.window_handles                                   
    driver.switch_to_window(other_tab_idx[0])  


def open_tab(address_queue, driver):
  print("open_tab")
  for address in address_queue:
    print("for",address)
    open_tab_script = "window.open(\""+address[0]+"\",\"_blank\");"                   
    driver.execute_script(open_tab_script)
    sleep(5)

  tab_idx_list = driver.window_handles
  print("address_qeueue",address_queue)
  print("tab_idx_list", tab_idx_list)

  tab = tuple(tab_idx_list)
  address = tuple(address_queue)

  print(address)
  tab_idx_tuple = zip(tab, address)
  for tab in tab_idx_tuple:
    print("tab", tab)
  
  return tab_idx_tuple


def crawl_tab(tab_list, driver):
    print("crawl_tab")
    tab_list = list(tab_list)
    for tab_idx_num in range(0, len(tab_list)):
       print(tab_idx_num)
       tab_idx = tab_list[tab_idx_num]
       print(tab_idx)
       switch_tab(driver, tab_idx)
       page_title = driver.title
       print(page_title)
       page_write(driver, page_title, tab_idx_num)
       #driver.close()


def page_write(driver, page_title, tab_idx_num):
    address_queue = list()
    if page_title != 'Problem loading page':                        
       print(page_title, " get source. tab index = ",tab_idx_num[0])                    
       address_queue.append(cur_date())          
       address_queue.append("live")               
       address_queue.append(str(torSelEnum.TB_SEL_SUCCESS.value))                       
       write_output_file(address_queue)
       write_html_file(driver, tab_idx_num[1])
    else:
      print("problem page")
      address_queue.append(cur_date())
      address_queue.append("dead")
      address_queue.append(str(torSelEnum.TB_SEL_UNDEFINED_EXCEPT.value))
      write_output_file(address_queue)


def write_html_file(driver, file_name):
    file_name = file_name + ".html"
    print(file_name)
    with codecs.open(OUTPUT_PATH["HTML_PATH"] + "/" + file_name,
                     "w", "utf-8") as html_writer:
       html_writer.write(driver.page_source)
    print("write complete", OUTPUT_PATH["HTML_PATH"] + "/" + file_name)


def switch_tab(driver,tab_idx):
  try:                                                            
     driver.switch_to_window(tab_idx)                            
  except SelWindowExcept:                                         
     crawler_logging("a","[TB_SEL_NO_SUCH_WINDOW_EXCEPT] : Current tab idx " \
     +str(tab_idx_list) + "\n Current Queue \n")             

    
def exit_crawler(driver, output_file):                               
    if driver:                                                                  
        driver.close()                                                          
    if XVFB_DISPLAY.is_alive():                                                 
        XVFB_DISPLAY.stop()                                                     
    if output_file:                                                             
        output_file.close()      


def open_write_file():
  output_file = open(OUTPUT_PATH["SERVER_LIVE_PATH"],'w')
  writer = csv.writer(output_file, delimiter='\t')
  return writer


def open_header_path():
  hs_header = open(OUTPUT_PATH["HEADER_PATH"], 'a')
  return hs_header


def main(path, timeout):
 # 준비
 make_path_dir(path)
 driver = open_tor_browser() 
 session = request_setup()
 print("SESSION:", session)

 writer = open_write_file()
 header_path = open_header_path()

 # 읽기
 reader_list = read_input()

 # 처리

 for address_idx in range(len(reader_list)):
   address_queue = list()
   row = reader_list[address_idx]
   onion_address = row[0]
   print("onion_address:", onion_address)
   hs_main_page_get(driver, onion_address)

   hs_status_code = hs_request_status_code(session, onion_address)
   print("hs_status_code:", hs_status_code)
   w_mode, status = write_status_code(hs_status_code, row)
   print("mode:", w_mode, "status:", status)

   if w_mode == 'a':
     print("write mode:", w_mode)
     address_queue.append(status)
   elif w_mode == 'w':
     print("write mode:", w_mode)
     write_output_file(status)

   tor_crawling(address_queue, driver, address_idx, len(reader_list))
 exit_crawler(driver, writer)


if __name__ == "__main__":
  #TODO ARG parse로 root directory 가져오기(여기엔 INPUT도 있어야함)
#  XVFB_DISPLAY.start()
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--rootdirectory", "-d", 
                      help = "root directory")
  parser.add_argument("--timeout", "-t",
                      help = "timeout")
  args = parser.parse_args()
  #TODO 찾아봐야할것 : rootdirectory
  main(args.rootdirectory, args.timeout)
 # if XVFB_DISPLAY.is_alive():
 #   XVFB_DISPLAY.stop()


