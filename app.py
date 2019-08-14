from flask import Flask, Response
from scrape import getEventCards
app = Flask(__name__)

import json

@app.route('/')
def hello_world():
    resp = Response(json.dumps(getEventCards(), ensure_ascii=False).encode('utf-8'))
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp
