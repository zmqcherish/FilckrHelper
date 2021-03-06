import flickrapi
from concurrent import futures
from urllib.request import urlretrieve
from db_helper import *
from util import *

base_uri = 'https://www.flickr.com/services/rest/'
api_key = ''
api_secret = ''
base_path = 'D:/cherish'

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
	sql = f'SELECT * from sets WHERE user_id="{user_id}"'
	done_sets = select_item(sql)
	done_set_ids = [a['id'] for a in done_sets]
	for s in sets:
		sid = s.attrib['id']
		if sid in done_set_ids:
			continue
		title = s.find('title').text
		photo_num = int(s.attrib['photos'])
		video_num = int(s.attrib['videos'])
		insert_set((sid, user_id, title, photo_num, video_num))
		yield sid

def get_set_photo(user_id, sid):
	# sid= '72157667936936671'
	url_type = 'url_o,url_h,url_l,url_c,url_z,url_n,url_m,url_t'
	count = 0
	for photo in flickr.walk_set(sid, extras=url_type):
		count += 1
		title = photo.get('title')
		url = ''
		# for _t in url_type.split(','):
		# 	url = photo.get(_t)
		# 	if url:
		# 		break
		# if not url:
		# 	continue
		# insert_img((photo.get('id'), title, url, user_id, sid))
	print(count)


def save_user_data():
	# user_id = '28859910@N02'
	user_id = '42758436@N05'
	sets = get_user_sets(user_id)
	# sql = 'SELECT * from sets WHERE user_id = "42758436@N05"'
	# sets = select_item(sql)
	sets1 = get_txt_file()
	for s in sets:
		sid = s['id']
		print(sid)
		if sid not in sets1:
			continue
		# if not start and sid != '72157655822769324':
			# continue
		# start = True
		get_set_photo(user_id, sid)
		# sleep(2)


def check_img_num():
	all_sets = get_all_data('sets')
	for s in all_sets:
		sid = s['id']
		n = s['photo_num'] + s['video_num']
		sql = f'select count(1) as num from img where set_id={sid}'
		num_res = select_item(sql)
		if num_res[0]['num'] != n:
			print(sid, num_res[0]['num'], n)


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


@except_decorative
def download_pic2(src, file_name, try_time=3):
	try:
		urlretrieve(src, file_name)
		return True
	except Exception as ex:
		if try_time > 0:
			return download_pic2(src, file_name, try_time - 1)
		print(ex)


def check_download_num(folder_path):
	data = os.listdir(folder_path)
	number_files = len(data)
	return number_files


def download_one_img(img):
	sid = img['set_id']
	iid = img['id']
	url = img['url_o']
	user_id = img['user_id']
	folder_path = f'{base_path}/{user_id}/{sid}'
	file_path = f'{folder_path}/{img["title"]}.jpg'
	file_path2 = f'{folder_path}/{sid}-{iid}.jpg'
	print(iid, file_path)
	# download_res = download_pic(url, file_path, file_path2)
	download_res = download_pic2(url, file_path2)
	if download_res:
		update_img(iid, sid)


def download_data():
	user_id = '28859910@N02'
	user_id = '42758436@N05'
	create_folder(f'{base_path}/{user_id}')
	sql = f'select * from sets where done=0'
	all_sets = select_item(sql)
	for s in all_sets:
		sid = s['id']
		title = s["title"]
		folder_path = f'{base_path}/{user_id}/{sid}'
		folder_res = create_folder(folder_path)
		if not folder_res:
			print(sid)
			continue
		sql = f'select * from img where set_id={sid} and done=0'
		res = select_item(sql)
		total_num = s['photo_num'] + s['video_num']
		check_num = check_download_num(folder_path)
		print(sid, title, total_num, check_num, len(res))
		if total_num == check_num and len(res) == 0:
			update_set(sid)
		if total_num != check_num and len(res) == 0:
			print(sid, title)

		if len(res) == 0:
			continue
		workers = min(10, len(res))
		with futures.ThreadPoolExecutor(workers) as executor:
			orders = executor.map(download_one_img, res)
		# for img in res:
		# 	download_one_img(img)

@except_decorative
def get_set_key(sid):
	data = {
			'set_id': sid,
			'extras': 'offline_enabled',
			'viewerNSID': '129791999@N08',
			'method': 'flickr.download.archives.create',
			'csrf': '1597953151:smy98krbxy:f3d72ae1ad93ec72e2f38cd7826c347e',
			'api_key': '46edcc1951297cf783eaf152065186ea',
			'format': 'json',
			'hermes': '1',
			'hermesClient': '1',
			'reqId': '76bba671',
			'nojsoncallback': '1'
	}
	headers = {
    'cookie': "xb=769770; AMCVS_48E815355BFE96970A495CD0%40AdobeOrg=1; s_cc=true; ffs=129699186-4114; cookie_session=129699186%3A2027c7e0aa619a5b4bc9e310aa5842c5; cookie_accid=129699186; cookie_epass=2027c7e0aa619a5b4bc9e310aa5842c5; sa=1602382708%3A129791999%40N08%3A4b3843f1806a5ac8e5d0210d2a535c8b; sp=61f58bad-1792-43ba-9de3-6524f299949a; __gads=ID=3c110fba88eff66c:T=1597198712:S=ALNI_Mb-LK1g8S4fmUM-HSrkeQ5rdhF7Ew; __ssid=0607c45bee8aa781bc7f23397650177; localization=zh-hk%3Bus%3Bhk; flrbp=1597842235-7ae9a5dfd54d4d83cd71eb90cfa8816a084a5190; flrbs=1597842235-0fe788abc7c33c071c6a42ea33c3a1ba336b5f67; flrbgrp=1597842235-3eedd82836cea3fd092a0fb10b744a65c6eddba6; flrbgdrp=1597842235-7a4905f45cb40986803486b9890a6ea668741681; flrbgmrp=1597842235-fe5af29ad7f77c8b4c2fb7ee6eead8d01c48aef8; flrbrst=1597842235-cee2493aae61ab63bc5589c1e4633ed43a574c2d; flrtags=1597842235-8ca1c848565505455d1bd8622abf42555663301a; flrbfd=1597842235-d30f7b2cd0b51ae614a55646db02d7b03ab4f78a; flrbrp=1597842235-0b82698ef5ce9aaf981c07e4106960d9c26c1e91; flrbrgs=1597842235-666078ab9cdddaf18e02f8fc00656b7ef0f3800e; adCounter=5; vp=1903%2C936%2C1%2C17%2Csearch-photos-everyone-view%3A1522%2Cphotolist-container%3A1522%2Cprofile-container%3A1522%2Cphotosof-container%3A1522%2Calbums-list-page-view%3A1522%2Calbum-page-view%3A1522; s_tp=6787; _sp_ses.df80=*; AMCV_48E815355BFE96970A495CD0%40AdobeOrg=281789898%7CMCMID%7C08839025225355913490893918737028835251%7CMCAAMLH-1598529157%7C11%7CMCAAMB-1598529157%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1597931557s%7CNONE%7CvVersion%7C4.1.0; s_ppv=albums-list-page-view%2C14%2C14%2C936; s_ptc=0.00%5E%5E0.00%5E%5E0.00%5E%5E0.00%5E%5E1.82%5E%5E0.27%5E%5E7.31%5E%5E0.02%5E%5E9.20; _sp_id.df80=4465da9e-71c3-4c73-aac5-a262c6ce43b0.1597198357.10.1597924427.1597890972.2c75277b-0917-4fd5-859f-27c0c3583f6f; s_sq=smugmugincflickrprodudction%3D%2526c.%2526a.%2526activitymap.%2526page%253Dalbums-list-page-view%2526link%253D%2525E5%2525BB%2525BA%2525E7%2525AB%25258B%2525E5%2525A3%252593%2525E7%2525B8%2525AE%2525E6%2525AA%252594%2525E6%2525A1%252588%2526region%253Dyui_3_16_0_1_1597924353565_4140%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    'authority': "api.flickr.com",
    'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
    'accept': "*/*",
    'origin': "https://www.flickr.com",
    'sec-fetch-site': "same-site",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'referer': f"https://www.flickr.com/photos/nickadel/albums/{sid}",
    'accept-language': "zh-CN,zh;q=0.9"
    }
	a =  requests.post('https://api.flickr.com/services/rest', headers=headers, params=data)
	return a.json()['archive']['key']


@except_decorative
def download_set(sid, key, down_path):
	if not key:
		return
	headers = {
    'cookie': "xb=769770; AMCVS_48E815355BFE96970A495CD0%40AdobeOrg=1; s_cc=true; ffs=129699186-4114; cookie_session=129699186%3A2027c7e0aa619a5b4bc9e310aa5842c5; cookie_accid=129699186; cookie_epass=2027c7e0aa619a5b4bc9e310aa5842c5; sa=1602382708%3A129791999%40N08%3A4b3843f1806a5ac8e5d0210d2a535c8b; sp=61f58bad-1792-43ba-9de3-6524f299949a; __gads=ID=3c110fba88eff66c:T=1597198712:S=ALNI_Mb-LK1g8S4fmUM-HSrkeQ5rdhF7Ew; __ssid=0607c45bee8aa781bc7f23397650177; localization=zh-hk%3Bus%3Bhk; flrbp=1597842235-7ae9a5dfd54d4d83cd71eb90cfa8816a084a5190; flrbs=1597842235-0fe788abc7c33c071c6a42ea33c3a1ba336b5f67; flrbgrp=1597842235-3eedd82836cea3fd092a0fb10b744a65c6eddba6; flrbgdrp=1597842235-7a4905f45cb40986803486b9890a6ea668741681; flrbgmrp=1597842235-fe5af29ad7f77c8b4c2fb7ee6eead8d01c48aef8; flrbrst=1597842235-cee2493aae61ab63bc5589c1e4633ed43a574c2d; flrtags=1597842235-8ca1c848565505455d1bd8622abf42555663301a; flrbfd=1597842235-d30f7b2cd0b51ae614a55646db02d7b03ab4f78a; flrbrp=1597842235-0b82698ef5ce9aaf981c07e4106960d9c26c1e91; flrbrgs=1597842235-666078ab9cdddaf18e02f8fc00656b7ef0f3800e; adCounter=5; vp=1903%2C936%2C1%2C17%2Csearch-photos-everyone-view%3A1522%2Cphotolist-container%3A1522%2Cprofile-container%3A1522%2Cphotosof-container%3A1522%2Calbums-list-page-view%3A1522%2Calbum-page-view%3A1522; s_tp=6787; _sp_ses.df80=*; AMCV_48E815355BFE96970A495CD0%40AdobeOrg=281789898%7CMCMID%7C08839025225355913490893918737028835251%7CMCAAMLH-1598529157%7C11%7CMCAAMB-1598529157%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1597931557s%7CNONE%7CvVersion%7C4.1.0; s_ppv=albums-list-page-view%2C14%2C14%2C936; s_ptc=0.00%5E%5E0.00%5E%5E0.00%5E%5E0.00%5E%5E1.82%5E%5E0.27%5E%5E7.31%5E%5E0.02%5E%5E9.20; _sp_id.df80=4465da9e-71c3-4c73-aac5-a262c6ce43b0.1597198357.10.1597924427.1597890972.2c75277b-0917-4fd5-859f-27c0c3583f6f; s_sq=smugmugincflickrprodudction%3D%2526c.%2526a.%2526activitymap.%2526page%253Dalbums-list-page-view%2526link%253D%2525E5%2525BB%2525BA%2525E7%2525AB%25258B%2525E5%2525A3%252593%2525E7%2525B8%2525AE%2525E6%2525AA%252594%2525E6%2525A1%252588%2526region%253Dyui_3_16_0_1_1597924353565_4140%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    'authority': "www.flickr.com",
    'upgrade-insecure-requests': "1",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'sec-fetch-site': "same-origin",
    'sec-fetch-mode': "navigate",
    'sec-fetch-user': "?1",
    'sec-fetch-dest': "document",
    'referer': f"https://www.flickr.com/mail/{sid}",
    'accept-language': "zh-CN,zh;q=0.9"
    }
	url = f'https://downloads.flickr.com/s/{key}.zip'
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		return False
	with open(down_path, 'wb') as f:
		f.write(r.content)
	# urlretrieve(url, down_path)
	return True

def get_zip_data():
	user_id = '42758436@N05'
	create_folder(f'{base_path}/{user_id}')
	fail_num = 0
	while True:
		sql = f'SELECT * from sets WHERE user_id = "{user_id}" and done=0'
		sets = select_item(sql)
		if len(sets) == 0:
			break
		for s in sets:
			sid = s['id']
			print(sid, fail_num)
			download_key = get_set_key(sid)
			down_path = f'{base_path}/{user_id}/{sid}.zip'
			res = download_set(sid, download_key, down_path)
			if res:
				update_set(sid)
				fail_num = 0
			else:
				sleep(fail_num * 10)
				fail_num += 1
			sleep(60)
# get_zip_data()
# save_user_data()
# check_img_num()
download_data()

