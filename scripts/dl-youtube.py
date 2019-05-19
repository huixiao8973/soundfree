# coding=UTF-8
import os
import logging

from pytube import YouTube


logger = logging.Logger("dy.log")


def download(url, target, codec=None):
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
    acodec = stream.audio_codec
    tmp_dir = "/tmp/"
    a_name = os.path.join(target, ".".join([title, acodec]))
    v_name = os.path.join(tmp_dir, stream.default_filename)
    

    # download video
    stream.download(tmp_dir)
    # split audio track
    cmd = 'ffmpeg -i "{vname}" -vn -acodec copy "{aname}"'.format(vname=v_name, aname=a_name)
    os.system(cmd)
    os.remove(v_name)
    # change audio codec
    if codec is not None:
        cmd = 'ffmpeg -i "{aname}" -c:a {codec} "{name}"'.format(
            aname=a_name, codec=codec, name='.'.join(a_name.split('.')[:-1]+[codec]))
        print(cmd)
        os.system(cmd)
        os.remove(a_name)


if __name__ == '__main__':
    import sys
    url, target = sys.argv[1], sys.argv[2]
    codec = sys.argv[3] if len(sys.argv) > 3 else None
    download(url, target, codec=codec)
