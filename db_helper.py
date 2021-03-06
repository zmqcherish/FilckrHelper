import sqlite3

data_file= 'data.db'

def exec_sql(db_file, sql, item, is_update=False):
	try:
		db = sqlite3.connect(db_file)
		with db:
			cursor = db.cursor()
			cursor.execute(sql) if is_update else cursor.execute(sql, item)
	except sqlite3.IntegrityError as ex:
		print('error', item)
	except Exception as ex:
		print(ex)
	finally:
		db.close()


def del_sql(db_file, sql):
	try:
		db = sqlite3.connect(db_file)
		with db:
			cursor = db.cursor()
			cursor.execute(sql)
	except sqlite3.IntegrityError:
		print('error')
	except Exception as ex:
		print(ex)
	finally:
		db.close()


def select_item_main(db_file, sql):
	try:
		db = sqlite3.connect(db_file)
		db.row_factory = sqlite3.Row
		with db:
			cursor = db.cursor()
			cursor.execute(sql)
			return list(cursor.fetchall())
	except sqlite3.IntegrityError:
		print('error')
	finally:
		db.close()


def select_item(sql):
	return select_item_main(data_file, sql)

def insert_data(sql, data):
	exec_sql(data_file, sql, data)


def insert_set(data):
	sql = '''INSERT INTO sets(id, user_id, title, photo_num, video_num) VALUES(?,?,?,?,?)'''
	insert_data(sql, data)


def insert_img(img):
	sql = '''INSERT INTO img(id, title, url_o, user_id, set_id) VALUES(?,?,?,?,?)'''
	insert_data(sql, img)


def get_all_data(table):
	return select_item(f'select * from {table}')

def update_set(sid):
	sql = f'update sets set done=1 where id = {sid}'
	exec_sql(data_file, sql, None, True)

def update_set2(sid):
	sql = f'update sets set zip=1 where id = {sid}'
	exec_sql(data_file, sql, None, True)

def update_img(_id, sid):
	sql = f'update img set done=1 where id = {_id} and set_id = {sid}'
	exec_sql(data_file, sql, None, True)
# check_exist('11')
# imgs = get_all_img()

# keys = []
# for img in imgs:
# 	if img['key'] in keys:
# 		print(img)
# 	else:
# 		keys.append(img['key'])