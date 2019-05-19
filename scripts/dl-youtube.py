# coding=UTF-8
import os
import re
import logging
import unicodedata

from pytube import YouTube
from pytube import Playlist


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validation_audio_codec(codec):
    if codec.startswith("mp4a"):
        # return "mp4a"
        # return 'aac'
        return 'm4a'
    else:
        return codec


def validate_chinese_name(songname):
    # trans chinese punctuation to english
    songname = unicodedata.normalize('NFKC', songname)
    songname = songname.replace('/', "%2F").replace('\"', "%22")
    rstr = r"[\/\\\:\*\?\"\<\>\|\+\-:;',=.?@]"
    # Replace the reserved characters in the song name to '-'
    rstr = r"[\/\\\:\*\?\"\<\>\|\+\-:;=?@]"  # '/ \ : * ? " < > |'
    return re.sub(rstr, "_", songname)


def download(url, target, codec=None):
    logger.info("Process %s" % url)
    # YouTube(url).streams.first().download(target)
    streams = YouTube(url).streams.all()
    if len(streams) == 0:
        logger.warn("Warnning: can not find any videos from %s" % url)
        return None
    # filter video that has no audio track
    streams = [item for item in streams if item.includes_audio_track]
    if len(streams) == 0:
        logger.warn("Warnning: can not find any streams in videos from %s" % url)
        return None
    # find highest quality audio
    stream = sorted(streams, key=lambda x: int(x.abr.strip('kbps')), reverse=True)[0]

    title = stream.player_config_args['title']
    acodec = validation_audio_codec(stream.audio_codec)
    tmp_dir = "/tmp/"
    a_name = os.path.join(target, ".".join([title, acodec]))
    v_name = os.path.join(tmp_dir, stream.default_filename)

    # download video
    stream.download(tmp_dir)
    # split audio track
    cmd = 'ffmpeg -y -i "{vname}" -vn -acodec copy "{aname}" >> ffmpegLogs.log 2>&1'.format(vname=v_name, aname=a_name)
    # cmd = 'ffmpeg -y -i {vname} -vn -acodec copy {aname} 2>&1 >> ffmpegLogs.log'.format(vname=v_name, aname=a_name)
    os.system(cmd)
    if os.path.isfile(v_name):
        os.remove(v_name)
    # change audio codec
    if codec is not None:
        cmd = 'ffmpeg -y -i "{aname}" -c:a {codec} "{name}" >> ffmpegLogs.log 2>&1'.format(
            aname=a_name, codec=codec, name='.'.join(a_name.split('.')[:-1]+[codec]))
        # cmd = 'ffmpeg -y -i {aname} -c:a {codec} {name} 2>&1 >> ffmpegLogs.log'.format(
        #     aname=a_name, codec=codec, name='.'.join(a_name.split('.')[:-1]+[codec]))
        logger.info(cmd)
        os.system(cmd)
        if os.path.isfile(a_name):
            os.remove(a_name)
    logger.info("Process %s job done" % url)


def download_playlist(url, target, codec=None):
    from concurrent.futures import ThreadPoolExecutor

    pl = Playlist(url)
    pl.populate_video_urls()
    urls = pl.video_urls
    with ThreadPoolExecutor(max_workers=len(urls)) as works:
        futures = []
        for item in urls:
            futures.append(works.submit(download, item, target, codec=codec))
        [item.result() for item in futures]
    print("All %d jobs Done." % len(urls))


if __name__ == '__main__':
    import sys
    url, target = sys.argv[1], sys.argv[2]
    codec = sys.argv[3] if len(sys.argv) > 3 else None

    if 'playlist' in url:
        download_playlist(url, target, codec=codec)
    else:
        download(url, target, codec=codec)
