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

from soundfree.baidumusic import fetch_albume_song_ids
from soundfree.baidumusic import download_song


logger = set_logger()


def main():
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


if __name__ == '__main__':
    main()

