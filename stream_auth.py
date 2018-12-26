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

from flask_oauthlib import client

REDIRECT_URI = '/oauth2callback'

with open('authorized_users.txt') as f:
  authorized_users = f.read().splitlines()
with open('client_secret.json') as f:
  config = json.loads(f.read())

app = flask.Flask('my demo')
camera = None
app.secret_key = config['app_secret']

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


@app.route('/image')
def capture_image():
  access_token = flask.session.get('access_token')        
  if access_token is None:
    callback = flask.url_for('authorized', _external=True)
    return google.authorize(callback=callback)

  camera.hflip = False
  camera.vflip = False
  camera.rotation = 0  # 0,90,180,270
  camera.capture('image.jpg')
  return 'OK'


@app.route('/video')
def record_video():
  access_token = flask.session.get('access_token')        
  if access_token is None:
    callback = flask.url_for('authorized', _external=True)
    return google.authorize(callback=callback)

  camera.start_recording(
      'video.h264', format='h264', resize=(640, 480), bitrate=1000000)
  for _ in range(10):
    now = datetime.datetime.now() 
    camera.annotate_text = '{0} - {1: %Y/%b/%d %H:%M:%S}'.format('Room', now)
    time.sleep(1)
  camera.stop_recording()
  return 'OK'


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
  camera.rotation = 180
  camera.annotate_background = picamera.color.Color('#777777')

  frame_count = 0

  stream = io.BytesIO()
  for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
    frame_count += 1
    stream.seek(0)
    data = stream.read()
    stream.seek(0)
    stream.truncate()

    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

    now = datetime.datetime.now()
    camera.annotate_text = '{0} - {1: %Y/%m/%d %H:%M:%S} - {2}'.format('Room', now, frame_count)

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


if __name__ == '__main__':
  try:
    global camera
    camera = picamera.PiCamera()
    app.run(host='0.0.0.0', port=8080, debug=False)
  finally:
    camera.close()
    print("closing camera")

