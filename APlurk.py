from graphics import *
import urllib, urllib2, cookielib, e32, appuifw




#Background
appuifw.app.screen='large' #Screen size(large)
img=Image.new((240,320)) #background
bgimage=Image.open("C:\\data\Images\\test.jpg") #Image path should be like C:\\data\Images\\test.jpg
appuifw.app.directional_pad = False
def handle_redraw(rect):
	canvas.blit(bgimage) #Drawing background
canvas=appuifw.Canvas(event_callback=None, redraw_callback=handle_redraw)
appuifw.app.body=canvas


#Menu functions
def send_message():
	pmessage = appuifw.query(u"Type message to plurk:", "text")
	post_to_plurk(pmessage);
	
def about():
    appuifw.note(u"Created by Itex & Xolvo", "info")
			
def quit():
    app_lock.signal()

def post_to_plurk(pmessage):
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	plurk_api_key = '5cZQnLGHJMmPRYsADiOq1x1wMuSkmocE'
	get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
	encode = urllib.urlencode
	try:
		fp = opener.open(get_api_url('/Users/login'),
			encode({'username': 's60test',
					'password': '1097',
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
#Menu list
appuifw.app.menu = [(u"Send Message", send_message),
                    (u"About", about),
					(u"Quit", quit)]

appuifw.app.exit_key_handler = quit # exit
app_lock = e32.Ao_lock()   #Exit
app_lock.wait() #prevent the application from closing before the user tells it to


