import solr_interaction
from solr_interaction import solr_instance
from flask import Flask, render_template, request

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def hello_world():
    return render_template('temp.html') 

@app.route('/search',  methods=['GET', 'POST'])
def search():
    query_string = request.form['search_input']
    results = solr_interaction.search_query(query_string, solr_instance)
    return render_template('temp.html', results = results)
    
app.debug = True
app.run()
