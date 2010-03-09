from graphics import *
import urllib, urllib2, cookielib, e32, appuifw, e32dbm, sysinfo, os

plurk_login = u'Plurk User'
plurk_password = 'lol'
path = u"C:\\data\python\\"
limg = None
limg_path = u''

#Background
if not appuifw.touch_enabled():
	appuifw.app.screen='large' #Screen size(large)
	img=Image.new((240,320)) #background
	bgimage=Image.open(path+"test.jpg") #Image path should be like C:\\data\Images\\test.jpg
else:
	appuifw.app.directional_pad = False
	appuifw.app.screen='normal' #Screen size(normal)
	img=Image.new((360,640)) #background
	bgimage=Image.open(path+"test_b.jpg") #Image path should be like C:\\data\Images\\test.jpg

def handle_redraw(rect):
	canvas.blit(bgimage) #Drawing background
canvas = appuifw.Canvas(event_callback=None, redraw_callback=handle_redraw)
appuifw.app.body = canvas

#Work with file
def write():  #define the write function to write in a database
	global plurk_login, plurk_password
	db = e32dbm.open(path+"settings.db","c") #open the file
	db[u"login"] = plurk_login
	db[u"password"] = plurk_password
	db[u"start_key"] = '0' #after first start = 0
	db.close()

def read():  #define a read function to read a database
	global plurk_login, plurk_password
	db = e32dbm.open(path+"settings.db","r") #open a file
	plurk_login = db[u"login"]  #read it using the dictionary concept. 
	plurk_password = db[u"password"]
	db.close()
	
#Menu functions
def send_message():
	pmessage = appuifw.query(u"Type message to plurk:", "text")
	post_to_plurk(pmessage);

def settings():
	global plurk_login, plurk_password
	plurk_login = appuifw.query(u"Enter login:", "text", unicode(plurk_login));
	plurk_password = appuifw.query(u"Enter password:", "code");
	write()
	appuifw.note(u"Saved!", "conf")
	
def about():
	appuifw.query(u"Created by \nItex & xolvo", "query")
	#appuifw.note(u"Created by Itex & Xolvo", "info")
	
def quit():
	app_lock.signal()
	write()

def post_to_plurk(pmessage):
	global plurk_login, plurk_password
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	plurk_api_key = '5cZQnLGHJMmPRYsADiOq1x1wMuSkmocE'
	get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
	encode = urllib.urlencode
	try:
		fp = opener.open(get_api_url('/Users/login'),
			encode({'username': plurk_login,
					'password': plurk_password,
					'api_key': plurk_api_key}))		
	except urllib2.URLError:
		appuifw.note(u"Logon Error", "error")
	try:
		fp = opener.open(get_api_url('/Timeline/plurkAdd'),
			encode({'content':pmessage.encode('utf-8'),
					'qualifier': 'says',
					'api_key': plurk_api_key}))
		appuifw.note(u"Posted!", "conf")
	except urllib2.URLError:
		appuifw.note(u"Posting Error", "error")

def add_pic_filesystem():
	global limg, limg_path
	if e32.in_emulator():
		imagedir = u'c:\\images'
	else:
		imagedir = u'e:\\images'
	
	images = list()
	files = map(unicode, os.listdir(imagedir))
	# save only images
	for x in files:
		if os.path.splitext(x)[1] in ('.jpg', '.png', '.gif'):
			images.append(x)
	
	index = appuifw.selection_list(images)
	limg = Image.open(imagedir + '\\' + images[index])
	limg_path = imagedir + '\\' + images[index]
	# Display image in the middle of screen
	canvas.blit(limg, target = ((canvas.size[0] - limg.size[0])/2, (canvas.size[1] - limg.size[1])/2))

def add_pic_photocamera():
	pass

read()
if plurk_password == 'lol':
	settings()

		
#Menu list
appuifw.app.menu = [(u"Plurk!", send_message),
					(u'Add picture',
						((u'From Gallery', add_pic_filesystem),
						(u'With your camera', add_pic_photocamera))
					),
					(u"Settings", settings),
					(u"About", about),
					(u"Quit", quit)]

appuifw.app.exit_key_handler = quit # exit
app_lock = e32.Ao_lock()   #Exit
app_lock.wait() #prevent the application from closing before the user tells it to


