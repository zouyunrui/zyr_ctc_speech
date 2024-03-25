import datetime
import random
import string

def get_filename():
    random_name = ''.join(random.choices(string.ascii_lowercase, k=5))
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]
    filename = f"{timestamp}-{random_name}"
    return filename
