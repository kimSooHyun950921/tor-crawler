#!/bin/bash
git pull tor develop
nohup /home/kimsoohyun/00-tor/02-data/00-tor_crawl_data/INPUT/TOR/tor > /dev/null 2>&1 &
python3 tor_crawler.py -d /home/kimsoohyun/00-tor/02-data/00-tor_crawl_data/ -t 120

