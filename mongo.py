# mongo.py

from flask import Flask,redirect
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import validators
from pyshorteners import Shortener
import os

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'

mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def get_all_stars():
  fetch = mongo.db.fetch
  output = []
  for s in fetch.find():
    output.append({'name' : s['name'], 'distance' : s['distance']})
  return jsonify({'result' : output})

# @app.route('/fetch', methods=['GET'])
# def get_one_star(name):
#   fetch = mongo.db.fetch
#   s = fetch.find_one({'name' : name})
#   if s:
#     output = {'name' : s['name'], 'distance' : s['distance']}
#   else:
#     output = "No such name"
#   return jsonify({'result' : output})

@app.route('/fetch/short-url', methods=['POST'])
def short_1():
  fetch = mongo.db.fetch
  long_url = request.json['long_url']
  if not validators.url(long_url):
    output = {"long_url":long_url, 'status' : "FAILED","status_codes":["INVALID_URLS"]}
  else:
    api_key = 'private'
    shortener = Shortener('Tinyurl')
    short_url=shortener.short(long_url)
    short_url=short_url.replace("http://tinyurl.com","hck.re")
    output = {"long_url":long_url,'short_url' : short_url, 'status' : "OK","status_codes":[]}
  return jsonify(output)


@app.route('/fetch/long-url', methods=['POST'])
def long_1():
  fetch = mongo.db.fetch
  short_url = request.json['short_url']
  # if not validators.url(long_url):
  #   output = {"long_url":long_url, 'status' : "FAILED","status_codes":["INVALID_URLS"]}
  # else:
  #   api_key = 'private'
  #   shortener = Shortener('Tinyurl')
  #   short_url=shortener.short(long_url)
  #   short_url=short_url.replace("http://tinyurl.com","hck.re")
  #   output = {"long_url":long_url,'short_url' : short_url, 'status' : "OK","status_codes":[]}
  shortener = Shortener('Tinyurl')
  short_url=short_url.replace("hck.re","http://tinyurl.com")

  long_url=shortener.expand(short_url)
  output = {"long_url":long_url, 'status' : "OK","status_codes":[]}

  return jsonify(output)

@app.route('/fetch/short-urls/', methods=['POST'])
def short_2():
  fetch = mongo.db.fetch
  long_urls = request.json['long_urls']
  short_urls={}
  invalid_urls=[]
  for i in long_urls:

    if not validators.url(i):
      invalid_urls.append(i)
    else:
      # api_key = 'private'
      shortener = Shortener('Tinyurl')
      short_url=shortener.short(i)
      short_url=short_url.replace("http://tinyurl.com","hck.re")
      short_urls[i]=short_url
  if invalid_urls!=[]:
    output = {"invalid_urls":invalid_urls, 'status' : "FAILED","status_codes":["INVALID_URLS"]}
    return jsonify(output)
  else:
    output = {'short_urls' : short_urls,"invalid_urls":[], 'status' : "OK","status_codes":[]}
    return jsonify(output)



@app.route('/fetch/long-urls/', methods=['POST'])
def long_2():
  fetch = mongo.db.fetch
  long_urls={}
  invalid_urls=[]
  short_urls = request.json['short_urls']
  for i in short_urls:
    try:
      shortener = Shortener('Tinyurl')
      i=i.replace("hck.re","http://tinyurl.com")

      long_url=shortener.expand(i)
      long_urls[i]=long_url
    except Exception:
      i=i.replace("http://tinyurl.com","hck.re")
      output = {"invalid_urls":[i], 'status' : "FAILED","status_codes":["SHORT_URLS_NOT_FOUND"]}
      return jsonify(output)
      

  if invalid_urls!=[]:
    output = {"invalid_urls":[], 'status' : "FAILED","status_codes":["SHORT_URLS_NOT_FOUND"]}
    return jsonify(output)
  else:
    output = {"long_urls":long_urls,"invalid_urls":[], 'status' : "OK","status_codes":[]}
    return jsonify(output)
  

  return jsonify(output)


@app.route('/<short_url_hash>/', methods=['POST'])
def short_3(short_url_hash):
  fetch = mongo.db.fetch
  url_to=short_url_hash
  shortener = Shortener('Tinyurl')
  url_to=url_to.replace("hck.re","http://tinyurl.com")

  long_url=shortener.expand(url_to)
  # return redirect(long_url, code=302)
  return jsonify({"q":url_to,"w":short_url_hash})
  

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port,debug=True)
    