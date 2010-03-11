from graphics import *
import e32, appuifw, e32dbm, os

plurk_login = u'Plurk User'
plurk_password = 'None'
limg = None
limg_path = u''

#Background
if not appuifw.touch_enabled():
	path = u"c:\\data\python\\"
	appuifw.app.screen = 'normal' #Screen size(large)
	bgimage = Image.open(path + "test.jpg") #Image path should be like C:\\data\Images\\test.jpg
	appuifw.app.title = u'Plurk App'
else:
	path = u"e:\\data\python\\"
	appuifw.app.directional_pad = False
	appuifw.app.screen = 'normal' #Screen size(normal)
	bgimage = Image.open(path + "test_b.jpg") #Image path should be like C:\\data\Images\\test.jpg
	appuifw.app.title = u'Plurk App'

def handle_redraw(rect = None):
	''' rect is a four-element tuple
	ex. (0, 0, 360, 487) '''
	canvas.blit(bgimage)
	if limg is not None:
		canvas.blit(limg, target = ((canvas.size[0] - limg.size[0])/2, (canvas.size[1] - limg.size[1])/2))

canvas = appuifw.Canvas(event_callback = None, redraw_callback = handle_redraw)
appuifw.app.body = canvas

#Work with file
def write():  #define the write function to write in a database
	global plurk_login, plurk_password
	if plurk_login and plurk_password is not None:
		db = e32dbm.open(path+"settings.db","c") #open the file
		db[u"login"] = plurk_login
		db[u"password"] = plurk_password
		db.close()
		return True
	
	return False


def read():  #define a read function to read a database
	global plurk_login, plurk_password
	db = e32dbm.open(path+"settings.db","c") #open a file
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
	
	if write():
		appuifw.note(u"Saved!", "conf")
	else:
		appuifw.note(u"Nothing to save.", "info")

def about():
	appuifw.query(u"Created by \nItex & xolvo", "query")
	
def quit():
	app_lock.signal()
	write()

def post_to_plurk():
	import urllib2, cookielib
	
	global plurk_login, plurk_password
	plurk_api_key = '5cZQnLGHJMmPRYsADiOq1x1wMuSkmocE'
	get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
	
	from sys import path as sysPath
	sysPath.append(path + 'lib') # special fix to import local modules
	import FileUploader, simplejson
	
	global plurk_login, plurk_password
	
	cookies = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies), FileUploader.MultipartPostHandler)
	
	try:
		fp = opener.open(get_api_url('/Users/login'),
							{'username': plurk_login,
							'password': plurk_password,
							'api_key': plurk_api_key})
		fp.read()
	except urllib2.HTTPError, e:
		print e.read()
		appuifw.note(u"Logon error", "error")
	
	if limg is not None:
		try:
			fp = opener.open(get_api_url('/Timeline/uploadPicture'),
								{'api_key' : plurk_api_key,
								'image' : open(limg_path, "rb")})
		except urllib2.HTTPError, e:
			print e.read()
			appuifw.note(u"Pic post error", "error")
			
		jsonobj = simplejson.loads(fp.read()) # Parse json to the dictionary object
	
	try: plText = ' '.join([jsonobj['thumbnail'], plurk_text])
	except NameError: plText = plurk_text
	
	try:
		fp = opener.open(get_api_url('/Timeline/plurkAdd'),
							{'content': plText.encode('utf-8'),
							'qualifier': qualifier if qualifier is not u'' else u':',
							'api_key': plurk_api_key})
		appuifw.note(u"Posted!", "conf")
	except urllib2.HTTPError, e:
		print e.read()
		appuifw.note(u"Plurk with pic posting error", "error")

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
	
	index = appuifw.popup_menu(images)
	limg = Image.open(imagedir + '\\' + images[index])
	limg_path = imagedir + '\\' + images[index]
	
	# Resize image
	if limg.size[0] > 360:
		limg = limg.resize((240, 400), callback = None, keepaspect = 1)
	
	# Optimize UI redraw
	canvas.begin_redraw()
	handle_redraw()
	canvas.end_redraw()
	
	# Display image in the middle of screen
	# canvas.blit(limg, target = ((canvas.size[0] - limg.size[0])/2, (canvas.size[1] - limg.size[1])/2))
	
def add_pic_photocamera():
	pass

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
		socket.set_default_access_point(pnts[index])
		return True;
	
	return False

while not select_access_point():
	pass

if os.path.exists(path+"settings.db.e32dbm"):
	read()
else:
	settings()
		
#Menu list
menu_list = [
				(u"Plurk!", post_to_plurk),
				(u'Add picture',
					((u'From Gallery', add_pic_filesystem),
					(u'With your camera', add_pic_photocamera))
				),
				(u'Add text', add_text_new),
				(u"Settings", settings),
				(u"About", about)
			]
appuifw.app.menu = menu_list

appuifw.app.exit_key_handler = quit # exit
app_lock = e32.Ao_lock()   #Exit
app_lock.wait() #prevent the application from closing before the user tells it to