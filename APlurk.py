from graphics import *
import e32, appuifw, os, key_codes, time
from e32dbm import open as db_open

from urllib2 import build_opener, HTTPError, HTTPCookieProcessor
from cookielib import CookieJar

# These strings do not influence or on the app cold boot
# either on the plurk posting.
from sys import path as sysPath
sysPath.append('e:\\data\python\\lib')
import FileUploader, simplejson

plurk_login = u'Plurk User'
plurk_password = 'None'

limg = None
limg_path = u''
touch = appuifw.touch_enabled()

#Background
# path = os.getcwd() + '\\'
# drive_letter = os.getcwd().split("\\")[0]
if not touch:
	path = u"c:\\data\python\\"
	appuifw.app.screen = 'normal' #Screen size(large)
	bgimage = Image.open(path + "bg.png") #Image path should be like C:\\data\Images\\test.jpg
	appuifw.app.title = u'PluPic'
else:
	path = u"e:\\data\python\\"
	appuifw.app.directional_pad = False
	appuifw.app.screen = 'normal' #Screen size(normal)
	bgimage = Image.open(path + "bg_b.png") #Image path should be like C:\\data\Images\\test.jpg
	appuifw.app.title = u'PluPic'

def handle_redraw(rect = None):
	''' rect is a four-element tuple
	ex. (0, 0, 360, 487) '''
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

#Work with file
def write():  #define the write function to write in a database
	# import e32dbm
	# from e32dbm import open as db_open
	global plurk_login, plurk_password
	if plurk_login and plurk_password is not None:
		db = db_open(path+"settings.db","c") #open the file
		db[u"login"] = plurk_login
		db[u"password"] = plurk_password
		db.close()
		return True
	
	return False

def read():  #define a read function to read a database
	# import e32dbm
	# from e32dbm import open as db_open
	global plurk_login, plurk_password
	db = db_open(path+"settings.db","r") #open a file
	plurk_login = db[u"login"]  #read it using the dictionary concept. 
	plurk_password = db[u"password"]
	db.close()

#Menu functions
def send_message():
	global plurk_text
	pmessage = appuifw.query(u"Type message to plurk:", "text")
	plurk_text = pmessage if pmessage is not None else ''

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
	appuifw.query(u"Created by \nItex & xolvo", "query")
	
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
	
	index = appuifw.popup_menu(pnts, u'Select default access point:')
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
			print fp.read()
		except HTTPError, e:
			print e.read()
			
	def update(self, text, qualifier = u':'):
		try:
			fp = self.opener.open(self.get_api_url('/Timeline/plurkAdd'),
								{'content': text.encode('utf-8'),
								'qualifier': qualifier,
								'api_key': self.api_key,
								"lang": "ru" })
			
			print fp.read()
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
		
		global plurk_text
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
	else:
		appuifw.note(u'Something goes wrong...', 'error')

def add_pic_filesystem():
	global limg, limg_path
	if e32.in_emulator():
		imagedir = u'c:\\data\\images'
	else:
		imagedir = u'e:\\images'
	
	images = list()
	files = map(unicode, os.listdir(imagedir))
	# save only images
	for x in files:
		if os.path.splitext(x)[1] in ('.jpg', '.png', '.gif'):
			images.append(x)
	
	index = appuifw.selection_list(images)
	if index is None:
		return
	
	limg = Image.open(imagedir + '\\' + images[index])
	limg_path = imagedir + '\\' + images[index]
	
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
txt = appuifw.Text()
plurk_text = u''
qualifier = u''
qualifiers = [u'loves', u'likes', u'shares', u'gives', u'hates', u'wants', u'has', u'will', u'asks', u'wishes',
            	u'was', u'feels', u'thinks', u'says', u'is', u':', u'freestyle', u'hopes', u'needs', u'wonders']
def save_plurk_text():
	global plurk_text
	# Has some issues if qualifiers was removed manually by user
	plurk_text = appuifw.app.body.get()[len(qualifier):].strip()
	
	if len(plurk_text) - len(qualifier) <= 140:
		# appuifw.note(u'Saved\n' + plurk_text, 'conf')
		# Return an old menu back
		appuifw.app.body = canvas
		appuifw.app.menu = menu_list
	else:
		appuifw.note(u'Your text is longer than 140 symbols', 'error')

def add_qualifier():
	global qualifiers, qualifier, txt
	index = appuifw.popup_menu(qualifiers)
	
	if index is not None:
		if qualifier is not u'':
			# Delete old qualifier and 2 spaces around + 1 space between qualifier and main plurk text
			txt.delete(0, len(qualifier) + 3)
		
		qualifier = qualifiers[index]
		txt.set_pos(0)
		txt.color = 0xffffff
		txt.highlight_color = 0x994215
		txt.style = appuifw.HIGHLIGHT_STANDARD
		txt.add(qualifier)
		
		txt.color = 0x000000
		txt.highlight_color = 0xffffff
		txt.style = appuifw.HIGHLIGHT_STANDARD
		txt.add(u' ')
	
def add_text_new():
	global txt
	appuifw.app.body = txt
	txt.color = 0x000000
	appuifw.app.menu = [(u'Save', save_plurk_text)] #, (u'Add qualifier', add_qualifier)]
''' end '''

if os.path.exists(path+"settings.db.e32dbm"):
	read()
else:
	settings()

#camera
images_dir="e:\\images\\" 
def add_pic_photocamera():
	import  camera
	global touch
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
		if day<10:
			day='0'+day
		if mon<10:
			mon='0'+mon
		if os.path.exists(images_dir+day+mon+str(time.localtime()[0])+'.jpg'):
			while os.path.exists(images_dir+day+mon+str(time.localtime()[0])+'('+str(i)+')''.jpg'):
				i=i+1
			else:
				filename=day+mon+str(time.localtime()[0])+'('+str(i)+')''.jpg'
		else:
			filename=day+mon+str(time.localtime()[0])+'.jpg'
		pict.save(images_dir+filename, quality=100)
		
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
		canvas.bind(key_codes.EButton1Down, None)
	
	camera.start_finder(vf, size=(320, 240))
	canvas.bind(key_codes.EKeySelect, take_picture)
	canvas.bind(key_codes.EButton1Down, take_picture) # ignored if there was no touch support
	appuifw.app.menu = [(u'Take picture', take_picture), (u'Cancel', camquit)]

#Menu list
menu_list = [
				(u"Plurk!", post_to_plurk),
				(u'Add picture',
					((u'From Gallery', add_pic_filesystem),
					(u'With your camera', add_pic_photocamera))
				),
				(u'Add text', add_text_new if touch else send_message),
				(u"Settings", settings),
				(u"About", about)
			]
appuifw.app.menu = menu_list

appuifw.app.exit_key_handler = quit #exit
app_lock = e32.Ao_lock() #Exit
app_lock.wait() #prevent the application from closing before the user tells it to