from flask import Flask, render_template, request, url_for, redirect
from jinja2 import Template, Environment, FileSystemLoader
from typing import Dict, Text
import random
import string
import validators
from redis import Redis
import os


file_loader=FileSystemLoader('templates')
env=Environment(loader=file_loader)
REDIS_HOST=os.getenv("REDIS_HOST", None)
redisclient = Redis(host=REDIS_HOST, port=6379, charset="utf-8", decode_responses=True)

app=Flask(__name__) 

urls = {}



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

def BorrarUrl(key):
    redisclient.hdel("UrlsLog", key)
    redisclient.hdel("Visits", key)

def BorrarTodos():
    links=redisclient.hgetall("UrlsLog")
    values=redisclient.hgetall("Visits")
    for i in links.items():
        redisclient.hdel("UrlsLog", i)
    for j in values.items():
        redisclient.hdel("Visits", j)


@app.route('/', methods=['GET', 'POST'])
def home():
    template = env.get_template('urlshortener.html')
    url=" "
    short=" "
    val= 0
    if request.method == 'POST':
        url = request.form['url']
        custom=request.form['customurl']
        if not url:
            url=" "
        else:
            if not custom: 
                shorturl=generarurl(url)
                short="http://127.0.0.1:5000/"+shorturl
                redisclient.hset("UrlsLog", shorturl, url)
                redisclient.hset("Visits", shorturl, val)
            else: 
                short="http://127.0.0.1:5000/"+custom
                redisclient.hset("UrlsLog", custom, url)
                redisclient.hset("Visits", custom, val)
    return template.render(url=url, short=short)

@app.route('/historial', methods=['GET', 'POST'])
def historial():
    template=env.get_template('historial.html')
    links=redisclient.hgetall("UrlsLog")
    print(redisclient.hgetall("UrlsLog"))
    return template.render(links=links) 

@app.route('/administrador', methods=['GET', 'POST'])
def administrador():
    template=env.get_template('administrador.html')
    links=redisclient.hgetall("UrlsLog")
    if request.method=="POST":
        key=request.form['borrarurl']
        BorrarUrl(key) 
    return template.render(links=links) 

@app.route('/stats', methods=['GET', 'POST'])
def visits():
    template=env.get_template('stats.html')
    links=redisclient.hgetall("Visits")
    return template.render(links=links) 

@app.route('/<link>', methods=['GET', 'POST'])
def enviar(link): 
    links=redisclient.hgetall("UrlsLog")
    value=redisclient.hget("Visits", link)
    value=int(value)
    value=value+1
    redisclient.hset("Visits", link, value)
    for i, k in links.items():
        if (i==link):
            return redirect(k, code=302)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)