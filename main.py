import flickrapi
from urllib.request import urlretrieve
from db_helper import *
from util import *

base_uri = 'https://www.flickr.com/services/rest/'
api_key = ''
api_secret = ''
base_path = 'imgs'

@except_decorative
def get_flickr_obj():
	data = get_txt_file('key.txt')
	if len(data) != 1:
		print()
		return
	global api_key, api_secret
	api_key, api_secret = data[0].split()
	# flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
	flickr = flickrapi.FlickrAPI(api_key, api_secret, format='etree')
	return flickr


def get_photos(sid):
	url = f'{base_uri}?method=flickr.photosets.getPhotos&api_key={api_key}&photoset_id={sid}&user_id={user_id}&format=json'
	res = requests.get(url)
	a=1

flickr = get_flickr_obj()

def get_user_all_set(user_id):
	res = []
	i = 1
	while True:
		sets = flickr.photosets.getList(user_id=user_id, per_page=500, page=i)
		data = sets.find('photosets').findall('photoset')
		if len(data) == 0:
			break
		res.extend(data)
		i += 1
	return res

def get_user_sets(user_id):
	sets = get_user_all_set(user_id)
	for s in sets:
		title = s.find('title').text
		photo_num = int(s.attrib['photos'])
		video_num = int(s.attrib['videos'])
		sid = s.attrib['id']
		insert_set((sid, user_id, title, photo_num, video_num))
		yield sid

def get_set_photo(user_id, sid):
	for photo in flickr.walk_set(sid, extras='url_c,url_o'):
		title = photo.get('title')
		url = photo.get('url_o')
		insert_img((photo.get('id'), title, url, user_id, sid))


def save_user_data():
	user_id = '28859910@N02'
	# user_id = '42758436@N05'
	sets = get_user_sets(user_id)
	for sid in sets:
		print(sid)
		get_set_photo(user_id, sid)
		sleep(2)


def check_img_num():
	all_sets = get_all_data('sets')
	for s in all_sets:
		sid = s['id']
		n = s['photo_num'] + s['video_num']
		sql = f'select count(1) as num from img where set_id={sid}'
		num_res = select_item(sql)
		if num_res[0]['num'] != n:
			print(sid)


@except_decorative
def download_pic(src, file_name, file_path2):
	try:
		i = 2
		new_name = file_name
		file_name_part = file_name.split(".")
		while os.path.isfile(new_name):
			new_name = f'{".".join(file_name_part[0: -1])}{i}.{file_name_part[-1]}'
			i += 1
		urlretrieve(src, new_name)
		return new_name
	except Exception as ex:
		try:
			urlretrieve(src, file_path2)
			return file_path2
		except Exception as ex1:
			print(ex1)
		print(ex)

def download_pic_fake(file_name, file_path2):
	try:
		i = 2
		new_name = file_name
		file_name_part = file_name.split(".")
		while os.path.isfile(new_name):
			new_name = f'{".".join(file_name_part[0: -1])}{i}.{file_name_part[-1]}'
			i += 1
		append_txt_file(new_name, '1')
		return new_name
	except Exception as ex:
		try:
			append_txt_file(file_path2, '1')
			return file_path2
		except Exception as ex1:
			print(ex1)
		print(ex)


def check_download_num(folder_path):
	data = os.listdir(folder_path)
	number_files = len(data)
	return number_files


def download_data():
	user_id = '28859910@N02'
	create_folder(f'{base_path}/{user_id}')
	sql = f'select * from sets where done=0'
	all_sets = select_item(sql)
	for s in all_sets:
		sid = s['id']
		title = s["title"]
		folder_path = f'{base_path}/{user_id}/{title}'
		folder_res = create_folder(folder_path)
		if not folder_res:
			continue
		sql = f'select * from img where set_id={sid} and done=0'
		res = select_item(sql)
		total_num = s['photo_num'] + s['video_num']
		check_num = check_download_num(folder_path)
		print(title, total_num, check_num, len(res))
		if total_num == check_num and len(res) == 0:
			update_set(sid)
		if total_num != check_num and len(res) == 0:
			print(sid, title)
		for img in res:
			iid = img['id']
			url = img['url_o']
			file_path = f'{folder_path}/{img["title"]}.jpg'
			file_path2 = f'{folder_path}/{sid}-{iid}.jpg'
			download_res = download_pic(url, file_path, file_path2)
			if download_res:
				update_img(iid, sid)


def handle_complict():
	sid = '72157690144527556'
	user_id = '28859910@N02'
	title = 'Umphang Wildlife Sancturay'
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
		# download_pic_fake(file_path, file_path2)
	
	data = os.listdir(pre_folder_path)
	fake_data = os.listdir(folder_path)
	res = [a for a in data if a not in fake_data]
	print(res)
# handle_complict()
download_data()

