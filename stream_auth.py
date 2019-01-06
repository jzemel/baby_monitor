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

from flask_socketio import SocketIO, send, emit
from flask_oauthlib import client

REDIRECT_URI = '/oauth2callback'

with open('authorized_users.txt') as f:
  authorized_users = f.read().splitlines()
with open('client_secret.json') as f:
  config = json.loads(f.read())

app = flask.Flask('my demo')
camera = None
app.secret_key = config['app_secret']
socketio = SocketIO(app)

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
    callback = flask.url_for('authorized', _external=True)
    return google.authorize(callback=callback)

  return flask.render_template('vid_client.html')


@app.route('/stream')
def stream_video():
  access_token = flask.session.get('access_token')
  if access_token is None and not hash_check.check(flask.request):
    callback = flask.url_for('authorized', _external=True)
    return google.authorize(callback=callback)

  return flask.Response(
      _stream_video(), mimetype='multipart/x-mixed-replace; boundary=frame')


def _stream_video():
  camera.resolution = (960, 540)
  camera.framerate = 30
  camera.rotation = 0
  camera.annotate_background = picamera.color.Color('#777777')

  FPS.frame_count = 0
  FPS.frame_start = datetime.datetime.now()
  signal = re.search(r'signal:.+\t-(\d\d)', subprocess.check_output(["iw","wlan0","station","dump"])).group(1)

  stream = io.BytesIO()
  for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
    FPS.frame_count += 1
    stream.seek(0)
    data = stream.read()
    stream.seek(0)
    stream.truncate()

    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

    now = datetime.datetime.now()
    camera.annotate_text = '{0} - {1: %Y/%m/%d %H:%M:%S} - {2} -{3} dbm'.format('Room', now, FPS.frame_count, signal)

    time.sleep(.1)

@app.route(REDIRECT_URI)
def authorized():
  resp = google.authorized_response()
  access_token = resp['access_token']
  user = google.get('userinfo', token=(access_token, '')).data
  if user['email'] in authorized_users:
    flask.session['access_token'] = access_token, ''
    flask.session['user'] = user
    return flask.redirect(flask.url_for('stream_video'))
  else:
    return "%s not authorized" % user['email']

@app.route('/api/tlm', methods=['GET'])
def get_tasks():
  #investigate collectd
  tlm = {}
  tlm['signal'] = re.search(r'signal:.+\t-(\d\d)', subprocess.check_output(["iw","wlan0","station","dump"])).group(1)
  tlm['cpu'] = psutil.cpu_percent()
  tlm['mem'] = "%d%% of %d MB" % (psutil.virtual_memory().percent, psutil.virtual_memory().total/1000000)
  tlm['disk'] = "%d%% of %d GB" % (psutil.disk_usage('/').percent, psutil.disk_usage('/').total/1000000000)
  #tlm['load'] = "not implemented"
  tlm['fps'] = FPS.getFPS()
  tlm['timestamp'] = datetime.datetime.now().strftime('%I:%M:%S - %d %b %Y')
  print("sending telemtry via REST")
  return flask.jsonify(tlm)

@socketio.on('get_tlm')
def get_tlm(time_sent):
  tlm = {}
  tlm['signal'] = re.search(r'signal:.+\t-(\d\d)', subprocess.check_output(["iw","wlan0","station","dump"])).group(1)
  tlm['cpu'] = psutil.cpu_percent()
  tlm['mem'] = "%d%% of %d MB" % (psutil.virtual_memory().percent, psutil.virtual_memory().total/1000000)
  tlm['disk'] = "%d%% of %d GB" % (psutil.disk_usage('/').percent, psutil.disk_usage('/').total/1000000000)
  tlm['load'] = "not implemented"
  tlm['fps'] = round(FPS.frame_count / ((datetime.datetime.now() - FPS.frame_start).total_seconds()),2)
  tlm['timestamp'] = datetime.datetime.now().strftime('%I:%M:%S - %d %b %Y')
  emit('tlm_json',json.dumps(tlm))
  print("sent telemtry")
  #network buffers?

if __name__ == '__main__':
  try:
    global camera
    print("initializing camera")
    camera = picamera.PiCamera()
    print("camera initialized")
    #socketio.run(app, host='0.0.0.0', port=8080, debug=False)
    socketio.run(app, host='0.0.0.0', port=8080, debug=False, certfile='cert.pem', keyfile='key.pem')
    #socketio.run(app, host='0.0.0.0', port=8080, debug=False, ssl_context=('cert.pem', 'key.pem'))
  finally:
    camera.close()
    print("closing camera")

