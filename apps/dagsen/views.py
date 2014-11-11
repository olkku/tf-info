from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.conf import settings
import json
import urllib2, urllib
import datetime, calendar

# Cache kept for
minutes = 10

cam_url =  settings.CAM_URL

def nextMeal():
  now = datetime.datetime.now()
  if now.weekday() > 5 or now.hour > 16:
    # Weekends and after 16 show next day
    return 1
  else:
    # Else show current day
    return 0

@cache_page(60 * minutes)
def index(request, language='sv'):
  day = nextMeal()

  try:
    response = urllib2.urlopen("http://api.teknolog.fi/taffa/%s/json/%d/"%(language, day))
  except:
    return HttpResponse("Unable to access lunch API.", status=500)

  try:
    menu = json.load(response)
  except ValueError as e:
    return HttpResponse("Error parsing json from api", status=500)

  menu['cachebuster'] = calendar.timegm(datetime.datetime.now().utctimetuple())

  return render_to_response('dagsen/index.html',menu,context_instance=RequestContext(request))

@cache_page(5)
def queuecam(request):
  stream=urllib.urlopen(cam_url)
  bytes=''
  for x in range(0, 1000):
    bytes+=stream.read(1024)
    a = bytes.find('\xff\xd8')
    b = bytes.find('\xff\xd9')
    if a!=-1 and b!=-1:
        jpg = bytes[a:b+2]
        bytes= bytes[b+2:]
        return HttpResponse(jpg, content_type="image/jpeg")

  return HttpResponse("Unable to access camera.", status=500)

