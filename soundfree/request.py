# coding=utf-8
import os
import re
import json
import unicodedata

from soundfree.log import set_logger


logger = set_logger()


def validate_chinese_name(songname):
    # trans chinese punctuation to english
    songname = unicodedata.normalize('NFKC', songname)
    songname = songname.replace('/', "%2F").replace('\"', "%22")
    rstr = r"[\/\\\:\*\?\"\<\>\|\+\-:;',=.?@]"
    # Replace the reserved characters in the song name to '-'
    rstr = r"[\/\\\:\*\?\"\<\>\|\+\-:;=?@]"  # '/ \ : * ? " < > |'
    return re.sub(rstr, "_", songname)


def download_stream_to_file(songlink, filename, minimum_size=1024*1024, force_update=False):
    import urllib

    with urllib.request.urlopen(songlink, timeout=10) as rf:
        size = rf.length
        # if 'Content-Length' in info:
        #     size = int(info['Content-Length'])
        if size is None:
            logger.warning("file not found in %s" % songlink)
            return None

        # too small file skipping
        if size < minimum_size:
            logger.warning("the size of %s (%r Mb) is less than %s Mb, skipping" %
                           (filename, size/1024/1024, minimum_size/1024/1024))
            return None
        # downloaded skipping
        elif not force_update and is_downloaded(filename, size):
            logger.info("%s is already downloaded, skipping." % filename)
            return None
        # downlad file
        else:
            logger.info("%s is downloading now, size %s Mb ......\n\n" % (filename, size/1024/1024))
            with open(filename, "wb") as code:
                code.write(rf.read())
            logger.info("%s finished downloading ......\n\n" % filename)


def is_downloaded(filename, size):
    return os.path.isfile(filename) and os.path.getsize(filename) == size
