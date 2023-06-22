import random, string, json
from types import SimpleNamespace
import datetime

def randstring():
	alphabet = list("abcdefghijklmnopqrstuvwxyz")
	return "".join([alphabet[random.randint(0, 25)] for i in range(10)])

def json_to_object(data): # Turn json data into an object
	return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

def obj_to_json(obj):
	return json.dumps(obj.__dict__)

def get_current_timestamp():
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp
