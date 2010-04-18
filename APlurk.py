import e32, appuifw, os, key_codes, time

from graphics import *
from e32dbm import open as db_open

from urllib2 import build_opener, HTTPError, HTTPCookieProcessor, urlopen
from cookielib import CookieJar

from datetime import date
from itertools import count

# These strings do not influence or on the app cold boot
# either on the plurk posting.
from sys import path as sysPath
sysPath.append('e:\\data\\python\\lib')
import FileUploader, simplejson

plurk_login = u'Plurk User'
plurk_password = 'None'
version = u'0_1_1015'

limg = None
limg_path = u''
touch = appuifw.touch_enabled()

# special workaround for a proper camera orientation
if touch:
	appuifw.app.orientation = 'landscape'
	import camera
	appuifw.app.orientation = 'portrait'
else:
	import camera

# path = os.getcwd() + '\\'
# drive_letter = os.getcwd().split("\\")[0]
if not touch:
	path = u"c:\\data\python\\"
	appuifw.app.screen = 'normal'
	bgimage = Image.open(path + "bg.png")
	appuifw.app.title = u'PluPic'
else:
	path = u"e:\\data\python\\"
	appuifw.app.directional_pad = False
	appuifw.app.screen = 'normal'
	bgimage = Image.open(path + "bg_b.png")
	appuifw.app.title = u'PluPic'

def handle_redraw(rect = None):
	''' rect is a four-element tuple
	ex. (0, 0, 360, 487) '''
	if rect is not None:
		if rect[2] > 360:
			return
	
	canvas.blit(bgimage)
	if limg is not None:
		if not touch:
			canvas.blit(limg, target = (26, 26))
		else:
			canvas.blit(limg, target = ((canvas.size[0] - limg.size[0]) / 2, 22))
			
			x1, y1 = ( (canvas.size[0] - limg.size[0])/2, 22 )
			x2, y2 = ( x1 + limg.size[0], y1 + limg.size[1] )
			canvas.rectangle((x1, y1, x2, y2), outline = 0xcccccc, width = 10)

canvas = appuifw.Canvas(event_callback = None, redraw_callback = handle_redraw)
appuifw.app.body = canvas

def write():
	global plurk_login, plurk_password
	if plurk_login and plurk_password is not None:
		db = db_open(path+"settings.db","c")
		db[u"login"] = plurk_login
		db[u"password"] = plurk_password
		db.close()
		return True
	
	return False

def read():
	global plurk_login, plurk_password
	db = db_open(path+"settings.db","r")
	plurk_login = db[u"login"]
	plurk_password = db[u"password"]
	db.close()

def verupdate():
	if not st_connected:
		while not select_access_point():
			pass
	file = "ver.txt"
	server = "http://plurk-s60app.googlecode.com/svn/trunk/"
	url= "http://plurk-s60app.googlecode.com/files/plupic_v"
	update = urlopen(server + file).read()
	
	if update == version:
		appuifw.note(u"You are using the latest version","info")
	else:
		data = appuifw.query(u"Update from\nv. " +version+" to\nv. "+update + u" ?" , "query")
		if data:
			internal_url = url + update + ".sis"
			b = 'BrowserNG.exe'
			e32.start_exe(b, ' "%s"' %internal_url)

def send_message():
	global plurk_text
	pmessage = appuifw.query(u"Type message to plurk:", "text", plurk_text)
	plurk_text = pmessage if pmessage is not None else ''

def delpic():
	global limg_path, limg
	data = appuifw.query(u"Delete current picture?" , "query")
	if data:
		if os.path.exists(limg_path):
			os.remove(limg_path)
			limg = None
			limg_path = u''
			handle_redraw()
def clear(confirmation = True):
	global limg, limg_path
	if confirmation:
		if appuifw.query(u"Clear current picture?" , "query"):
			limg = None
			limg_path = u''
			handle_redraw()
	else:
		limg = None
		limg_path = u''
		handle_redraw()

def settings():
	global plurk_login, plurk_password
	settings_fields = [(u"Login", 'text', unicode(plurk_login)),
					   (u"Password", 'text' , u"****")]
	#Create an instance of Form
	settings_form = appuifw.Form(settings_fields, flags=appuifw.FFormDoubleSpaced)
	
	#Execute the form
	settings_form.execute()
	
	#After the form is saved and closed, display the information
	if settings_form[1][2] == u"****":
		pass
	else:
		plurk_login = settings_form[0][2]
		plurk_password = settings_form[1][2]
		if os.path.exists(path+"settings.db.e32dbm"):
			os.remove(path+"settings.db.e32dbm")
		write()
		appuifw.note(u"Saved!", "conf")

def about():
	appuifw.query(u"Created by \nItex & xolvo\nv. "+version, "query")
	
def quit():
	app_lock.signal()
	
st_connected = False
def select_access_point():
	''' Return True if selected, False otherwise '''
	import btsocket, socket
	global st_connected
	
	pnts = []
	points = btsocket.access_points()
	for i in points:
		pnts.append(i['name'])
	
	index = appuifw.popup_menu(pnts, u'Select access point:')
	if index is not None:
		try:
			socket.set_default_access_point(pnts[index])
			st_connected = True
			return True
		except:
			pass
	
	return False

from threading import Thread
class PlurkAPI:
	def __init__(self, api_key):
		self.get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
		self.opener = build_opener(HTTPCookieProcessor(CookieJar()), FileUploader.MultipartPostHandler)
		self.api_key = api_key
	
	def login(self, login, password, data = True):
		try:
			fp = self.opener.open(self.get_api_url('/Users/login'),
								{'username': login,
								'password': password,
								'api_key': self.api_key,
								'no_data': '1' if not data else ''})
			#print fp.read()
		except HTTPError, e:
			print e.read()
			
	def update(self, text, qualifier = u':'):
		try:
			fp = self.opener.open(self.get_api_url('/Timeline/plurkAdd'),
								{'content': text.encode('utf-8'),
								'qualifier': qualifier,
								'api_key': self.api_key,
								"lang": "ru" })
			
			#print simplejson.loads(fp.read())['content']
			return True
		except HTTPError, e:
			print e.read()
	
	def upload_image(self, imgpath):
		try:
			fp = self.opener.open(self.get_api_url('/Timeline/uploadPicture'),
								{'api_key' : self.api_key,
								'image' : open(imgpath, "rb")})
			
			return simplejson.loads(fp.read())['full']
		except HTTPError, e:
			print e.read()
	
class ThreadAPI(Thread):
	def __init__(self):
		Thread.__init__(self)
		
		self.functions = []
		self.args = ()
		
		self.returned_val = None
		
	def run(self):
		for count, f in enumerate(self.functions):
			self.returned_val = apply(f, self.args[count])
			
		return self.returned_val
	
	def init_targets(self, functions, args = ()):
		for func in functions:
			self.functions.append(func)
		
		try:
			self.args = args
		except:
			print 'error: can not init this'
			
class ProgressBar:
	def __init__(self, canvas, sprite_path = 'e:\\data\\python\\sprite.png', frame_size = (117, 40)):
		self.canvas = canvas
		self.sprite = Image.open(sprite_path)
		self.layer = Image.new(self.canvas.size)
		
		self.curr_frame = 0
		self.frame_w = frame_size[0]
		self.frame_h = frame_size[1]
		
		self.loader_pos = ( (self.layer.size[0] - self.frame_w) / 2, (self.layer.size[1] - self.frame_h) / 2)
		self.busy = True
		
		self.is_toush = appuifw.touch_enabled()
			
	def draw_frame(self, frame_number):
		self.layer.blit(self.sprite, target = self.loader_pos, source = ((frame_number * self.frame_w, 0),
																		((frame_number + 1) * self.frame_w, self.frame_h)))
		
		if self.is_toush:
			self.canvas.begin_redraw()
			self.canvas.blit(self.layer)
			self.canvas.end_redraw()
		else:
			self.canvas.blit(self.layer)

def post_to_plurk():
	if not st_connected:
		while not select_access_point():
			pass
	
	progress_bar = ProgressBar(canvas, path + 'sprite.png')
	thread_api = ThreadAPI()
	plurk_api = PlurkAPI('5cZQnLGHJMmPRYsADiOq1x1wMuSkmocE')
	
	global plurk_text
	
	if limg is not None:		
		upload_thread = ThreadAPI()
		
		upload_thread.init_targets([plurk_api.login, plurk_api.upload_image], args = ((plurk_login, plurk_password, False), (limg_path, )))
		upload_thread.start()
		
		iter = 0
		while upload_thread.isAlive():
			progress_bar.draw_frame(iter)
			
			if iter == 2:
				iter = 0
			else:
				iter += 1
				
			e32.ao_sleep(0.4)
		
		plurk_text = ' '.join([upload_thread.returned_val, plurk_text])
	
	thread_api.init_targets([plurk_api.login, plurk_api.update], args = ((plurk_login, plurk_password, False), (plurk_text, )))
	thread_api.start()
	
	iter = 0
	while thread_api.isAlive():
		progress_bar.draw_frame(iter)
		
		if iter == 2:
			iter = 0
		else:
			iter += 1
			
		e32.ao_sleep(0.4)
			
	handle_redraw()
	if thread_api.returned_val:
		appuifw.note(u'Posted!', 'conf')
		
		plurk_text = u''
		clear(confirmation = False)
	else:
		appuifw.note(u'Something goes wrong...', 'error')

def myComp (x,y):
    import re
    def getNum(str): return float(re.findall(r'\d+',str)[0])
    return cmp(getNum(x),getNum(y))
def add_pic_filesystem():
	global limg, limg_path
	imagedir = u'e:\\images'
	images = []
	full_path = []
	files = map(unicode, os.listdir(imagedir))
	# save only images
	for x in files:
		if os.path.splitext(x)[1] in ('.jpg', '.png', '.gif'):
			images.append(x)
	full_path = map(lambda x: imagedir + '\\' + x, images)
	full_path.sort(key=lambda x: os.path.getmtime(x), reverse = True)
	index = appuifw.selection_list(map(lambda x: os.path.split(x)[1], full_path))
	if index is None:
		return
	
	limg = Image.open(full_path[index])
	limg_path = full_path[index]
	
	# Resize image
	if limg.size[0] > 360:
		if not touch:
			limg = limg.resize((188, 143), callback = None, keepaspect = 1)
		else:
			limg = limg.resize((320, 240), callback = None, keepaspect = 1)
	# Optimize UI redraw
	canvas.begin_redraw()
	handle_redraw()
	canvas.end_redraw()
	
	# Display image in the middle of screen
	if not touch:
		canvas.blit(limg, target = (26,26))
	

''' Text field start functions '''
plurk_text = u''

def save_plurk_text():
	global plurk_text
	plurk_text = appuifw.app.body.get()
	
	if len(plurk_text) <= 140:
		# Return an old menu back
		appuifw.app.body = canvas
		appuifw.app.menu = menu_list
	else:
		appuifw.note(u'Your text is longer than 140 symbols', 'error')
	
def add_text_new():
	appuifw.app.body = txt = appuifw.Text()
	txt.color = 0x000000
	appuifw.app.menu = [(u'Save', save_plurk_text)]
''' end '''

if os.path.exists(path+"settings.db.e32dbm"):
	read()
else:
	settings()

#camera
class TouchCamera:
	def __init__(self, canvas, save_path = 'e:\\images\\'):
		self.canvas = canvas
		self.path = save_path
		
		self.mod = 'auto'
		
		self.toolbar = None #Image.new((160, 360))
		
		appuifw.app.screen = 'full'
		appuifw.app.orientation = 'landscape'
		
	def __filename_gen(self):
		today = date.today().strftime('%d%m%Y')

		for i in count(1):
			path_n = self.path + today + '%(#)03d' % {'#': i} + '.jpg'
			
			if not os.path.exists(path_n):
				return path_n
		
	def start_vf(self, frame):
		self.canvas.begin_redraw()
		
		canvas.blit(frame)
		self.__redraw_toolbar()
		
		self.canvas.end_redraw()
		
	def save(self, pos = (0, 0)):
		self.canvas.bind(key_codes.EButton1Down, None)
		img = camera.take_photo(mode = 'JPEG_Exif', flash = self.mod, size = (640, 480))
		
		save_p = self.__filename_gen()
		f = open(save_p, 'wb')
		f.write(img)
		f.close()
		
		#img = camera.take_photo(mode = 'RGB', flash = self.mod, size = (640, 480))
		#img.save(self.path + 'test.jpg', quality = 100, compression = 'no')
		
		self.close()
		
		global limg, limg_path
		limg_path = save_p
		limg = Image.open(save_p)
		limg = limg.resize((320, 240), callback = None, keepaspect = 1)
		handle_redraw()
	
	def close(self, pos = (0, 0)):
		self.canvas.bind(key_codes.EButton1Down, None)
		
		appuifw.app.screen = 'normal'
		appuifw.app.orientation = 'portrait'
		
		camera.stop_finder()
		camera.release()
		
	def flash_mod(self, pos = (0, 0)):
		flash_mods_items = map(unicode, camera.flash_modes())
		item = appuifw.popup_menu(flash_mods_items)
		
		if item is not None:
			self.mod = flash_mods_items[item]
	
	def make_toolbar(self, callable_items, toolbar_img_path = u'e:\\data\\python\\camera_toolbar.png'):
		'''
		@param callable_items: is a list of dictionaries [{'callback': function, 'area': ((0, 0), (10, 10))}, ...]
		'''
		self.toolbar = Image.open(toolbar_img_path)		
		self.canvas.blit(self.toolbar, target = (480, 0))
		
		for item in callable_items:
			self.canvas.bind(key_codes.EButton1Down, item['callback'], item['area'])
			
	def __redraw_toolbar(self):
		self.canvas.blit(self.toolbar, target = (480, 0))

images_dir="e:\\images\\" 
def add_pic_photocamera():
	def vf(im):
		if not touch:
			canvas.blit(im)
		else:
			canvas.begin_redraw()
			
			canvas.blit(bgimage)
			canvas.blit(im, target = ((canvas.size[0] - im.size[0]) / 2, 22))
			
			canvas.end_redraw()
	def save_picture(pict):
		global limg, limg_path
		
		day=str(time.localtime()[2])
		mon=str(time.localtime()[1])
		i=1
		if int(day) < 10:
			day = '0' + day
		if int(mon) < 10:
			mon = u'0' + mon
		if os.path.exists(images_dir+day+mon+str(time.localtime()[0])+'.jpg'):
			while os.path.exists(images_dir+day+mon+str(time.localtime()[0])+'('+str(i)+')''.jpg'):
				i=i+1
			else:
				filename=day+mon+str(time.localtime()[0])+'('+str(i)+')''.jpg'
		else:
			filename=day+mon+str(time.localtime()[0])+'.jpg'
		pict.save(images_dir+filename, quality=75)
		
		camquit()
		
		limg = Image.open(images_dir+filename)		
		if canvas.size[0] == 360:
			limg = limg.resize((320, 240), callback = None, keepaspect = 1)
			#canvas.blit(limg, target = ((canvas.size[0] - limg.size[0]) / 2, 22))
			handle_redraw()
		else:
			canvas.blit(bgimage)
			limg = limg.resize((188, 143), callback = None, keepaspect = 1)
			canvas.blit(limg, target = (26, 26))
		limg_path=images_dir+filename
	def take_picture(pos = (0, 0)): # For touch events support
		pic = camera.take_photo(size = (640, 480))
		save_picture(pic)
	def camquit():
		camera.stop_finder()
		camera.release()
		# get main menu back
		appuifw.app.menu = menu_list
		# clean all bindings
		canvas.bind(key_codes.EKeySelect, None)
	
	if touch:
		cam = TouchCamera(canvas)
		camera.start_finder(cam.start_vf, size = (503, 360))
		
		callbacks =[{'callback': cam.close, 'area': ((480, 1), (640, 71))},
					{'callback': cam.save, 'area': ((480, 73), (640, 143))},
					{'callback': cam.flash_mod, 'area': ((480, 145), (640, 215))}]
		
		cam.make_toolbar(callbacks)
	else:
		camera.start_finder(vf, size=(320, 240))
		canvas.bind(key_codes.EKeySelect, take_picture)
		
		appuifw.app.menu = [(u'Take picture', take_picture), (u'Cancel', camquit)]

#Menu list
menu_list = [
				(u"Plurk!", post_to_plurk),
				(u'Picture',
					((u'From Gallery', add_pic_filesystem),
					(u'From Camera', add_pic_photocamera),
					(u'Clear', clear),
					(u'Delete', delpic))
				),
				(u'Add text', add_text_new if touch else send_message),
				(u'Settings', 
					((u'Login', settings),
					(u'Check for updates', verupdate))
				),
				(u"About", about)
			]
appuifw.app.menu = menu_list

appuifw.app.exit_key_handler = quit
app_lock = e32.Ao_lock()
app_lock.wait()