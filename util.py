import sys
import requests
import logging
import pickle
import os
import subprocess
# import lxml.etree as ET
from time import sleep
from datetime import datetime, timedelta

today = datetime.today()
today_zero = datetime(today.year, today.month, today.day, 0, 0, 0)
yeaterday_zero = today_zero + timedelta(days=-1)

def except_decorative(func):
	def decorator(*args, **keyargs):
		try:
			return func(*args, **keyargs)
		except Exception as e:
			logging.error(f'handle {func.__name__} error: {e}')
	return decorator
	
def get_txt_file(file_path='1.txt'):
	content = ''
	with open(file_path, encoding='utf8') as txt_file:
		content = txt_file.readlines()
	return [c.strip('\n') for c in content]


def save_pickle(file_path, data):
	with open(file_path, 'wb') as f:
		pickle.dump(data, f)

@except_decorative
def get_pickle_file(file_path):
	with open(file_path, 'rb') as f:
		return pickle.load(f)

def save_xml_file(file_path, data):
	data.getroottree().write(file_path)

@except_decorative
def get_xml_file(file_path):
	return ET.parse(file_path)

@except_decorative
def create_folder(path):
	if os.path.exists(path):
		return True
	os.mkdir(path)
	return True

def append_txt_file(save_item, file_path='1.txt', end='\n'):
	with open(file_path, 'a', encoding='utf8') as txt_file:
		txt_file.write(save_item + end)

@except_decorative
def zip_folder(zf_name, path):
	zf_name += '.7z'
	a = subprocess.call(['7z', 'a', zf_name, path + "/*"])
	res = a == 0
	if not res:
		os.remove(zf_name)
	return res
# zip_folder('imgs/28859910@N02/test', 'imgs/28859910@N02/Doi Lang')