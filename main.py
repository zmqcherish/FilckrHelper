import flickrapi
from concurrent import futures
from urllib.request import urlretrieve
from db_helper import *
from util import *
import shutil

base_uri = 'https://www.flickr.com/services/rest/'
api_key = ''
api_secret = ''
base_path = 'C:/Users/zmqch/Downloads/imgs/'
user_id = '94853888@N04'	# ching
user_path = base_path + user_id

browser_cookies = 'xb=717461; AMCVS_48E815355BFE96970A495CD0%40AdobeOrg=1; AMCV_48E815355BFE96970A495CD0%40AdobeOrg=281789898%7CMCMID%7C54703930200875468001756492966735920348%7CMCAAMLH-1617768651%7C11%7CMCAAMB-1617768651%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1617171051s%7CNONE%7CvVersion%7C4.1.0; s_cc=true; sp=29f53d4a-c64b-4f60-977a-2d1078a1a359; __ssid=42cd032d0e13c7711de2d93764da142; notice_behavior=implied,eu; usprivacy=1---; euconsent-v2=CPD558VPD558VAvACBZHBSCgAAAAAAAAAAAAAAAAAAAA.YAAAAAAAAAAA; notice_preferences=0:; notice_gdpr_prefs=0:; cmapi_gtm_bl=ga-ms-ua-ta-asp-bzi-sp-awct-cts-csm-img-flc-fls-mpm-mpr-m6d-tc-tdc; cmapi_cookie_privacy=permit 1 required; liqph=811; liqpw=1504; ffs=129699186-9601; cookie_session=129699186%3A2027c7e0aa619a5b4bc9e310aa5842c5; cookie_accid=129699186; cookie_epass=2027c7e0aa619a5b4bc9e310aa5842c5; sa=1622351219%3A129791999%40N08%3Ab547bd0f23c2a217571c087b6de443db; localization=zh-hk%3Bus%3Bhk; flrbp=1617167219-9151a13f144e28389fdf89a420c2dd7239e781aa; flrbs=1617167219-616a955a9f7a2f7ca278949a3531dd5ad70ccd47; flrbgrp=1617167219-2e726e9ebfb1b94130628d4e88fae3a430acdcf7; flrbgdrp=1617167219-cedf9347049a9666881aa6c1c9311ae9618281ba; flrbgmrp=1617167219-995a742cd73d95aabd96725b2aa363b3b33fc74b; flrbrst=1617167219-d62843316a44947f83df4839da60fb9276f16e70; flrtags=1617167219-54110bdc70a8b6eeb4d5296ba2db3368f706d82e; flrbfd=1617167219-ce9c18528e813a58dc39d71006efb7938303329b; flrbrp=1617167219-cf284198a8268f41442bbafd97178cd949ae6c61; flrbrgs=1617167219-14536afd56a285da83bad3cf155b7ecbbf205a94; flrb=56; _ga=GA1.2.2104986945.1617167297; _gid=GA1.2.609099653.1617167297; ccc=%7B%22managed%22%3A0%2C%22changed%22%3A0%2C%22info%22%3A%7B%22cookieBlock%22%3A%7B%22level%22%3A0%2C%22blockRan%22%3A1%7D%7D%7D; s_ptc=%5B%5BB%5D%5D; vp=1487%2C843%2C1.5%2C17%2Calbums-list-page-view%3A1190%2Cphotolist-container%3A1190%2Ctag-photos-everyone-view%3A1190; s_tp=2657; s_ppv=albums-list-page-view%2C47%2C32%2C1260; _sp_ses.df80=*; _sp_id.df80=7f1913d5-8eb2-470e-8d5c-470731d78d49.1617163852.3.1617172421.1617168490.5bb1b65a-b5a6-4b89-9585-88058562c397; s_sq=smugmugincflickrprodudction%3D%2526c.%2526a.%2526activitymap.%2526page%253Dalbums-list-page-view%2526link%253D%2525E5%2525BB%2525BA%2525E7%2525AB%25258B%2525E5%2525A3%252593%2525E7%2525B8%2525AE%2525E6%2525AA%252594%2525E6%2525A1%252588%2526region%253Dyui_3_16_0_1_1617167891348_7069%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c'

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

# 从filckr api获取用户图集
def get_user_all_set():
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


def save_user_sets():
	sets = get_user_all_set()
	sql = f'SELECT * from sets WHERE user_id="{user_id}"'
	save_sets = select_item(sql)
	save_set_ids = [a['id'] for a in save_sets]
	for s in sets:
		sid = s.attrib['id']
		if sid in save_set_ids:
			continue
		title = s.find('title').text
		photo_num = int(s.attrib['photos'])
		video_num = int(s.attrib['videos'])
		insert_set((sid, user_id, title, photo_num, video_num))
		a=1
		# yield sid

# 从filckr api获取图片
def get_set_photo(sid):
	# sid= '72157667936936671'
	url_type = 'url_o,url_h,url_l,url_c,url_z,url_n,url_m,url_t'
	count = 0
	for photo in flickr.walk_set(sid, extras=url_type):
		count += 1
		title = photo.get('title')
		url = ''
		for _t in url_type.split(','):
			url = photo.get(_t)
			if url:
				break
		if not url:
			continue
		insert_img((photo.get('id'), title, url, user_id, sid))
		a=1
	print(count)

# 保存用户图片
def save_user_img():
	sql = f'SELECT * from sets WHERE user_id = "{user_id}"'
	sets = select_item(sql)
	# sets1 = get_txt_file()
	for s in sets:
		sid = s['id']
		print(sid)
		# if sid not in sets1:
		# 	continue
		# if not start and sid != '72157655822769324':
			# continue
		# start = True
		get_set_photo(sid)
		# sleep(2)


def check_img_num():
	all_sets = get_all_data('sets')
	for s in all_sets:
		if s['user_id'] != user_id:
			continue
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
def download_pic2(src, temp_path, file_name, try_time=3):
	try:
		urlretrieve(src, temp_path)
		shutil.move(temp_path, file_name)
		return True
	except Exception as ex:
		if try_time > 0:
			return download_pic2(src, temp_path, file_name, try_time - 1)
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
	temp_path = f'temp/{sid}-{iid}.jpg'
	print(iid, file_path)
	# download_res = download_pic(url, file_path, file_path2)
	download_res = download_pic2(url, temp_path, file_path2)
	if download_res:
		update_img(iid, sid)


def download_data():
	create_folder(user_path)
	sql = f'select * from sets where done=0 and user_id="{user_id}"'
	all_sets = select_item(sql)
	for s in all_sets:
		sid = s['id']
		title = s["title"]
		folder_path = f'{user_path}/{sid}'
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
		workers = min(20, len(res))
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
			'csrf': '1617196690:1wyg8wrkavw:15cafff2a493f4ed7e58ec8e545f3c44',
			'api_key': 'e31ccf3de71925b07ec6b3770380aded',
			'format': 'json',
			'hermes': '1',
			'hermesClient': '1',
			'reqId': '400742a0',
			'nojsoncallback': '1'
	}
	headers = {
		'cookie': browser_cookies,
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
	a = requests.post('https://api.flickr.com/services/rest', headers=headers, params=data)
	return a.json()['archive']['key']


@except_decorative
def download_set(sid, key, down_path):
	if not key:
		return
	headers = {
		'cookie': 'xb=717461; AMCVS_48E815355BFE96970A495CD0%40AdobeOrg=1; s_cc=true; sp=29f53d4a-c64b-4f60-977a-2d1078a1a359; __ssid=42cd032d0e13c7711de2d93764da142; notice_behavior=implied,eu; usprivacy=1---; euconsent-v2=CPD558VPD558VAvACBZHBSCgAAAAAAAAAAAAAAAAAAAA.YAAAAAAAAAAA; notice_preferences=0:; notice_gdpr_prefs=0:; cmapi_gtm_bl=ga-ms-ua-ta-asp-bzi-sp-awct-cts-csm-img-flc-fls-mpm-mpr-m6d-tc-tdc; cmapi_cookie_privacy=permit 1 required; liqph=811; liqpw=1504; ffs=129699186-9601; cookie_session=129699186%3A2027c7e0aa619a5b4bc9e310aa5842c5; cookie_accid=129699186; cookie_epass=2027c7e0aa619a5b4bc9e310aa5842c5; sa=1622351219%3A129791999%40N08%3Ab547bd0f23c2a217571c087b6de443db; localization=zh-hk%3Bus%3Bhk; flrbp=1617167219-9151a13f144e28389fdf89a420c2dd7239e781aa; flrbs=1617167219-616a955a9f7a2f7ca278949a3531dd5ad70ccd47; flrbgrp=1617167219-2e726e9ebfb1b94130628d4e88fae3a430acdcf7; flrbgdrp=1617167219-cedf9347049a9666881aa6c1c9311ae9618281ba; flrbgmrp=1617167219-995a742cd73d95aabd96725b2aa363b3b33fc74b; flrbrst=1617167219-d62843316a44947f83df4839da60fb9276f16e70; flrtags=1617167219-54110bdc70a8b6eeb4d5296ba2db3368f706d82e; flrbfd=1617167219-ce9c18528e813a58dc39d71006efb7938303329b; flrbrp=1617167219-cf284198a8268f41442bbafd97178cd949ae6c61; flrbrgs=1617167219-14536afd56a285da83bad3cf155b7ecbbf205a94; flrb=56; _ga=GA1.2.2104986945.1617167297; _gid=GA1.2.609099653.1617167297; ccc=%7B%22managed%22%3A0%2C%22changed%22%3A0%2C%22info%22%3A%7B%22cookieBlock%22%3A%7B%22level%22%3A0%2C%22blockRan%22%3A1%7D%7D%7D; s_ptc=%5B%5BB%5D%5D; _sp_ses.df80=*; vp=1504%2C860%2C1.5%2C17%2Calbums-list-page-view%3A1190%2Cphotolist-container%3A1190%2Ctag-photos-everyone-view%3A1190; _sp_id.df80=7f1913d5-8eb2-470e-8d5c-470731d78d49.1617163852.3.1617172753.1617168490.5bb1b65a-b5a6-4b89-9585-88058562c397; AMCV_48E815355BFE96970A495CD0%40AdobeOrg=281789898%7CMCMID%7C54703930200875468001756492966735920348%7CMCAAMLH-1617777554%7C11%7CMCAAMB-1617777554%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1617179954s%7CNONE%7CvVersion%7C4.1.0; s_tp=860; s_ppv=download-page-view%2C100%2C100%2C860; s_sq=smugmugincflickrprodudction%3D%2526c.%2526a.%2526activitymap.%2526page%253Ddownload-page-view%2526link%253D%2525E4%2525B8%25258B%2525E8%2525BC%252589%252520zip%252520%2525E6%2525AA%252594%2525E6%2525A1%252588%2526region%253Dyui_3_16_0_1_1617172752400_92%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c',
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

def download_zip_data():
	create_folder(user_path)
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
			down_path = f'{user_path}/{sid}.zip'
			res = download_set(sid, download_key, down_path)
			if res:
				update_set2(sid)
				fail_num = 0
			else:
				sleep(fail_num * 10)
				fail_num += 1
			sleep(60)

def show_download_name():
	folder_name = os.listdir(user_path)
	set_ids = ','.join(folder_name)
	sql = f"select * from sets where id in ({set_ids})"
	all_sets = select_item(sql)
	for s in all_sets:
		print(s['id'], s['title'])

# save_user_sets()
# save_user_img()
# check_img_num()
# download_zip_data()
# download_data()
# show_download_name()

