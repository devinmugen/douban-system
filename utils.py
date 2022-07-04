import time


def log(*args, **kwargs):
    format_time = '%H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format_time, value)
    with open('log.txt', 'a', encoding='utf-8') as f:
        print(dt, *args, file=f, **kwargs)
