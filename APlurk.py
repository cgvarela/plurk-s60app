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
touch = True if appuifw.touch_enabled() else False # Increase code efficiency

#Background
# path = os.getcwd() + '\\'
# drive_letter = os.getcwd().split("\\")[0]
if not touch:
	path = u"c:\\data\python\\"
	appuifw.app.screen = 'normal' #Screen size(large)
	bgimage = Image.open(path + "bg.png") #Image path should be like C:\\data\Images\\test.jpg
	appuifw.app.title = u'Plurk App'
else:
	path = u"e:\\data\python\\"
	appuifw.app.directional_pad = False
	appuifw.app.screen = 'normal' #Screen size(normal)
	bgimage = Image.open(path + "bg_b.jpg") #Image path should be like C:\\data\Images\\test.jpg
	appuifw.app.title = u'Plurk App'

def handle_redraw(rect = None):
	''' rect is a four-element tuple
	ex. (0, 0, 360, 487) '''
	canvas.blit(bgimage)
	if limg is not None:
		if not touch:
			canvas.blit(limg, target = (26, 26))
		else:
			canvas.blit(limg, target = (20, 22))

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

def post_to_plurk():
	# import urllib2
	'''from urllib2 import build_opener
	from urllib2 import HTTPError
	from urllib2 import HTTPCookieProcessor
	from cookielib import CookieJar'''
	
	# Not needed in the sis package
	'''from sys import path as sysPath
	sysPath.append(path + 'lib')
	import FileUploader, simplejson'''
	
	global plurk_login, plurk_password
	plurk_api_key = '5cZQnLGHJMmPRYsADiOq1x1wMuSkmocE'
	get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
	
	cookies = CookieJar()
	opener = build_opener(HTTPCookieProcessor(cookies), FileUploader.MultipartPostHandler)
	
	try:
		fp = opener.open(get_api_url('/Users/login'),
							{'username': plurk_login,
							'password': plurk_password,
							'api_key': plurk_api_key})
		fp.read()
	except HTTPError, e:
		print e.read()
		appuifw.note(u"Logon error", "error")
	
	if limg is not None:
		try:
			fp = opener.open(get_api_url('/Timeline/uploadPicture'),
								{'api_key' : plurk_api_key,
								'image' : open(limg_path, "rb")})
		except HTTPError, e:
			print e.read()
			appuifw.note(u"Pic post error", "error")
			
		jsonobj = simplejson.loads(fp.read()) # Parse json to the dictionary object
	
	try: plText = ' '.join([jsonobj['full'], plurk_text])
	except NameError: plText = plurk_text
	
	try:
		fp = opener.open(get_api_url('/Timeline/plurkAdd'),
							{'content': plText.encode('utf-8'),
							'qualifier': qualifier if qualifier is not u'' else u':',
							'api_key': plurk_api_key,
							"lang": "ru" })
		appuifw.note(u"Posted!", "conf")
	except HTTPError, e:
		print e.read()
		appuifw.note(u"Plurk with pic posting error", "error")

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
	
	index = appuifw.popup_menu(images)
	if index is None:
		return
	
	limg = Image.open(imagedir + '\\' + images[index])
	limg_path = imagedir + '\\' + images[index]
	
	# Resize image
	if limg.size[0] > 360:
		if touch==False:
			limg = limg.resize((188, 143), callback = None, keepaspect = 1)
		else:
			limg = limg.resize((310, 233), callback = None, keepaspect = 1)
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

def select_access_point():
	''' Return True if selected, False otherwise '''
	import btsocket, socket
	
	pnts = []
	points = btsocket.access_points()
	for i in points:
		pnts.append(i['name'])
	
	index = appuifw.popup_menu(pnts, u'Select default access point:')
	if index is not None:
		try:
			socket.set_default_access_point(pnts[index])
			return True
		except:
			pass
	
	return False

while not select_access_point():
	pass
if os.path.exists(path+"settings.db.e32dbm"):
	read()
else:
	settings()

#camera
images_dir="e:\\images\\" 
def add_pic_photocamera():
	import  camera
	
	def vf(im):
		if not touch:
			canvas.blit(im, target = (26, 26))
		else:
			canvas.begin_redraw()
			
			canvas.blit(bgimage)
			canvas.blit(im, target = (20, 22))
			
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
		pict.save(images_dir+filename, quality=90)
		
		camquit()
		
		limg = Image.open(images_dir+filename)		
		if canvas.size[0] == 360:
			limg = limg.resize((320, 240), callback = None, keepaspect = 1)
			canvas.blit(limg, target = (20, 22))
		else:
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