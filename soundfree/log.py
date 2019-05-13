# coding=utf-8
import logging


def set_logger(log_level=logging.INFO, log_file="download.log", log_format=None):
    if log_format is None:
        log_format = '%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s'
    logger = logging.getLogger()
    logger.setLevel(log_level)
    formatter = logging.Formatter(fmt=log_format, datefmt='%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
