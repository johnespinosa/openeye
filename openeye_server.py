import solr_interaction
from solr_interaction import solr_instance
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, render_template, json, jsonify, request
import flask
from flask.helpers import make_response
import flask.views
from flask.wrappers import Request

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def homepage_endpoint():
    return render_template('temp.html') 

def add_similar_articles(results):
    for result in results:
        related_articles = solr_interaction.get_similar_articles(int(result['id']), solr_instance)
        result['related'] = related_articles

@app.route('/search',  methods=['GET', 'POST'])
def search_endpoint():
    query_string = request.form['search_input']
    results = solr_interaction.search_query(query_string, solr_instance)
    add_similar_articles(results)
    return render_template('temp.html', results = results)
    
app.debug = True
app.run()
    
