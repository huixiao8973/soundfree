#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json
import os
import sys
import time
from multiprocessing.dummy import Pool

from soundfree.log import set_logger
from soundfree.request import validate_chinese_name
from soundfree.request import download_stream_to_file


logger = set_logger()


BAIDU_MUSIC_API = "http://music.baidu.com/data/music/fmlink"
BAIDU_SUGGESTION_API = 'http://sug.music.baidu.com/info/suggestion'


def fetch_albume_song_ids(url):
    import requests
    logger.info("fetching baidumusic song list from " + url + "\n")
    r = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36'})
    contents = r.text
    res = r'<ul class="f-hide">(.*?)</ul>'
    res = r'href="\/song\/(\d+)"'
    mm = re.findall(res, contents, re.S | re.M)
    return mm


def get_songid(value):
   payload = {'word': value, 'version': '2', 'from': '0'}
   value = value.replace('\\xa0', ' ')  # windows cmd 的编码问题
   logger.info(value)

   r = requests.get(BAIDU_SUGGESTION_API, params=payload)
   contents = r.text
   d = json.loads(contents, encoding="utf-8")
   if d is not None and 'data' not in d:
       return ""
   else:
       songid = d["data"]["song"][0]["songid"]
       logger.info("find songid: %s" % songid)
       return songid

def get_song_info(songid, song_type="flac"):
    import urllib
    payload = {'songIds': songid, 'type': song_type}
    params = urllib.parse.urlencode(payload)
    with urllib.request.urlopen(BAIDU_MUSIC_API+"?"+params) as rf:
        contents = rf.read().decode('utf-8')
        info = json.loads(contents, encoding="utf-8")
    return info


def download_song(songid, target_dir):
    song_info = get_song_info(songid)

    songname = song_info["data"]["songList"][0]["songName"]
    songname = validate_chinese_name(songname)

    artistName = song_info["data"]["songList"][0]["artistName"]
    artistName = validate_chinese_name(artistName)

    songlink = song_info["data"]["songList"][0]["songLink"]

    filename = ("%s/%s-%s.flac" %
                (target_dir, songname, artistName))
    logger.info("start donwload %s from %s" % (filename, songlink))
    download_stream_to_file(songlink, filename)


if __name__ == '__main__':
    start = time.time()
    if len(sys.argv) < 2:
         print("请在 python3 后加上要下载专辑的 url\n")
         print("示例: python3 main.py 'http://music.163.com/#/playlist?id=145258012'\n")
         exit()
    if len(sys.argv) >= 3:
        DOWNLOAD_DIR = sys.argv[2]
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)

    url = re.sub("#/", "", sys.argv[1]).strip()

    song_ids = fetch_albume_song_ids(url)
    logger.info("found %s song in albume: %s" % (len(song_ids), song_ids))
    
    # p = Pool()
    for songid in song_ids:
        if songid == "":
            continue
        # p.apply_async(download_song, args=(songid, DOWNLOAD_DIR))
        download_song(songid, DOWNLOAD_DIR)
    logger.info("\n================================================================\n")
    logger.info('Waiting for all download subprocesses done...')
    # p.join()
    # p.close()

    logger.info("\n================================================================\n")
    logger.info("Download finish!\nSongs' directory is %s/%s" % (os.getcwd(), DOWNLOAD_DIR))
    logger.info("cost %s s", str(time.time() - start))
