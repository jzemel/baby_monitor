# Comments, by Jon Zemel
#
# 

import datetime
import flask
import picamera
import time
import io
import json
import sys
import hash_check
import FPS
import subprocess
import re
import psutil

from flask_oauthlib import client

REDIRECT_URI = '/oauth2callback'
FILE_PATH = '/home/pi/baby_monitor/'

with open(FILE_PATH + 'authorized_users.txt') as f:
  authorized_users = f.read().splitlines()
with open(FILE_PATH + 'client_secret.json') as f:
  config = json.loads(f.read())
  #replace with flask.jsonify

app = flask.Flask('yo Orli')
camera = None
app.secret_key = config['app_secret']
port = config['port']
def_rotation = config['rotation']
def_width = config['width']

oauth = client.OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=config['client_id'],
    consumer_secret=config['client_secret'],
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

FPS = FPS.FPS_tracker()

@app.route('/home')
def home():
  access_token = flask.session.get('access_token')
  if access_token is None and not hash_check.check(flask.request):
    callback = flask.url_for('authorized', _external=True)+'/home'
    return google.authorize(callback=callback)

  return flask.render_template('vid_client.html')
  #return flask.send_from_directory(FILE_PATH, 'templates/vid_client.html')

@app.route('/stream')
def stream_video():
  access_token = flask.session.get('access_token')
  if access_token is None and not hash_check.check(flask.request):
    callback = flask.url_for('authorized', _external=True)+'/stream_video'
    return google.authorize(callback=callback)

  return flask.Response(
      _stream_video(flask.request.args), mimetype='multipart/x-mixed-replace; boundary=frame')


def _stream_video(args):
  try:
    camera.close()
    print("checking for existing cams")
    sleep(2)
  except (AttributeError, NameError):
    print("no camera open yet")
    global camera
  print("initializing camera")
  camera = picamera.PiCamera()
  width = int(args.get('width')) if args.get('width') else def_width
  height = int(args.get('height')) if args.get('height') else width * 9/16
  rotation = int(args.get('rotation')) if args.get('rotation') else def_rotation
  print("%dx%d, rot=%d" % (width,height, rotation))
  camera.resolution = (width, height)
  camera.framerate = 30 #TODO not sure if this does anything
  camera.rotation = rotation
  camera.annotate_background = picamera.color.Color('#777777')

  FPS.frame_count = 0
  FPS.frame_start = datetime.datetime.now()
  signal = re.search(r'signal:.+\t-(\d\d)', subprocess.check_output(["iw","wlan0","station","dump"])).group(1)

  stream = io.BytesIO()
  try:
    for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True, thumbnail=None):
      FPS.frame_count += 1
      stream.seek(0)
      data = stream.read()
      stream.seek(0)
      stream.truncate()

      yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

      now = datetime.datetime.now()
      camera.annotate_text = '{0} - {1: %Y/%m/%d %H:%M:%S} - {2} -{3} dbm'.format('Room', now, FPS.frame_count, signal)

      #time.sleep(.1)
  except picamera.exc.PiCameraAlreadyRecording:
    print("already recording!")
    camera.close()

  finally:
    camera.close()

@app.route(REDIRECT_URI)
@app.route(REDIRECT_URI + '/<page>')
def authorized(page='home'):
  resp = google.authorized_response()
  access_token = resp['access_token']
  user = google.get('userinfo', token=(access_token, '')).data
  if user['email'] in authorized_users:
    flask.session['access_token'] = access_token, ''
    flask.session['user'] = user
    return flask.redirect(flask.url_for(page))
  else:
    return "%s not authorized" % user['email']

@app.route('/api/tlm', methods=['GET'])
def get_tlm():
  access_token = flask.session.get('access_token')
  if access_token is None and not hash_check.check(flask.request):
    callback = flask.url_for('authorized', _external=True)+'/get_tlm'
    return google.authorize(callback=callback)

  tlm = {}
  tlm['signal'] = re.search(r'signal:.+\t-(\d\d)', subprocess.check_output(["iw","wlan0","station","dump"])).group(1)
  tlm['cpu'] = psutil.cpu_percent()
  tlm['mem'] = "%d%% of %d MB" % (psutil.virtual_memory().percent, psutil.virtual_memory().total/1000000)
  tlm['disk'] = "%d%% of %d GB" % (psutil.disk_usage('/').percent, psutil.disk_usage('/').total/1000000000)
  tlm['fps'] = FPS.getFPS()
  tlm['cpu_temp'] = psutil.sensors_temperatures()['cpu-thermal'][0].current
  tlm['time'] = datetime.datetime.now().strftime('%I:%M:%S - %d %b %Y')
  return flask.jsonify(tlm)
  #network buffers?

@app.errorhandler(500)
def internal_error(error):
  print("caught 500!")
  return "500 error", 500


if __name__ == '__main__':
  try:
    # global camera
    # print("initializing camera")
    # camera = picamera.PiCamera()
    # print("camera initialized")
    app.run(host='0.0.0.0', port=port, debug=False, ssl_context=(FILE_PATH + 'cert.pem', FILE_PATH + 'key.pem'))
  finally:
    camera.close()
    print("closing camera")

