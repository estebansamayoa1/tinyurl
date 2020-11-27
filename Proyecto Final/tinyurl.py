from flask import Flask, render_template, request, url_for, redirect
from jinja2 import Template, Environment, FileSystemLoader
from typing import Dict, Text
import random
import string
import validators
from redis import Redis


file_loader=FileSystemLoader('templates')
env=Environment(loader=file_loader)

redisclient = Redis(host='localhost', port=6379, charset="utf-8", decode_responses=True)

app=Flask(__name__)

def generarurl(url):
    if not url:
        return " "
    else:
        if (validators.url(url)==True):
            indexlength = 8
            possible_characters = "abcdefghijklmnopqrstuvwxyz1234567890"
            random_choices = [random.choice(possible_characters) for i in range(indexlength)]
            index = "".join(random_choices)
            return index
        else:
            return "Link Invalido"
        
            


@app.route('/', methods=['GET', 'POST'])
def home():
    template = env.get_template('urlshortener.html')
    url=" "
    short=" "
    if request.method == 'POST':
        url = request.form['url']
        custom=request.form['customurl']
        if not url:
            url=" "
        else:
            if not custom: 
                shorturl=generarurl(url)
                redisclient.hset("UrlsLog", shorturl, url)
                short="http://127.0.0.1:5000/"+shorturl
            else: 
                redisclient.hset("UrlsLog", custom, url)
                short="http://127.0.0.1:5000/"+custom
    return template.render(url=url, short=short)

@app.route('/historial', methods=['GET', 'POST'])
def historial():
    template=env.get_template('historial.html')
    links=redisclient.hgetall("UrlsLog")
    return template.render(links=links)

@app.route('/<link>')
def enviar(link): 
    links=redisclient.hgetall("UrlsLog")
    for i, k in links.items():
        if (i==link):
            return redirect(k, code=302)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)