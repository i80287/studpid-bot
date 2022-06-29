""" from time import *
print(time(), int(time()))
print(gmtime(time()))
print(localtime(time())) """
""" from datetime import tzinfo, timedelta, timezone, datetime
tzinfo = timezone(timedelta(hours=12))
print(datetime.fromtimestamp(1233333123-3600*5, tz=tzinfo)) """
""" from random import randint
while True:
    print(randint(0, 1))
    input() """