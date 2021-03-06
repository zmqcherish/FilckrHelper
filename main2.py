import flickrapi
from urllib.request import urlretrieve
from db_helper import *
from util import *

base_uri = 'https://www.flickr.com/services/rest/'
api_key = ''
api_secret = ''
base_path = 'imgs'

def download_pic_fake(file_name, file_path2):
	try:
		i = 2
		new_name = file_name
		file_name_part = file_name.split(".")
		while os.path.isfile(new_name):
			new_name = f'{".".join(file_name_part[0: -1])}{i}.{file_name_part[-1]}'
			i += 1
		append_txt_file('1', new_name)
		return new_name
	except Exception as ex:
		try:
			append_txt_file('1', file_path2)
			return file_path2
		except Exception as ex1:
			print(ex1)
		print(ex)


def handle_img_complict():
	sid = '72157631540292214'
	user_id = '28859910@N02'
	sql = f'select * from sets where id="{sid}"'
	title_res = select_item(sql)
	title = title_res[0]['title']
	pre_folder_path = f'{base_path}/{user_id}/{title}'
	title += '-fake'
	folder_path = f'{base_path}/{user_id}/{title}'
	create_folder(folder_path)
	sql = f'select * from img where set_id="{sid}"'
	res = select_item(sql)
	for img in res:
		iid = img['id']
		file_path = f'{folder_path}/{img["title"]}.jpg'
		file_path2 = f'{folder_path}/{sid}-{iid}.jpg'
		download_pic_fake(file_path, file_path2)
	
	data = os.listdir(pre_folder_path)
	fake_data = os.listdir(folder_path)
	res1 = [a for a in data if a not in fake_data]
	res2 = [a for a in fake_data if a not in data]
	print(res1, res2)


def handle_zip_complict():
	sql = f'select * from sets where zip=1'
	res = select_item(sql)
	data = [a['title'] + '.7z' for a in res]
	data2 = os.listdir('D:/zip')
	res1 = [a for a in data if a not in data2]
	res2 = [a for a in data2 if a not in data]
	print(res1, res2)


def zip_data():
	# base_zip_path = 'D:/GitHub/MyProject/FilckrHelper/imgs/'
	base_zip_path = 'C:/Users/zhiqiangdong/OneDrive/志强Surface/flickr/imgs/'
	user_id = '28859910@N02'
	zip_path_all = base_zip_path + user_id
	# folders = os.listdir(zip_path_all)

	sql = f'select * from sets where done=1 and zip=0'
	res = select_item(sql)
	for r in res:
		folder = r['title']
		zip_path = f'{zip_path_all}/{folder}'
		zip_name = f'D:/zip/{folder}'
		# zip_name = f'{base_zip_path}{user_id}-zip/{folder}'
		zip_res = zip_folder(zip_name, zip_path)
		if zip_res:
			update_set2(r['id'])
zip_data()
# handle_zip_complict()
# handle_img_complict()

