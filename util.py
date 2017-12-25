import datetime


## Utility Functions ##
def printt(msg):
   time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   print("{}| {}".format(time_str, msg))

