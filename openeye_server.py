import json
from solr_interaction import solr_instance, search_query
from flask import Flask, render_template, request

app = Flask(__name__)
app.config.from_object(__name__)

def are_crowdflower_related(titles_str):
    titles = titles_str.split("|")
    title1 = titles[0]
    title2 = titles[1]
    
    with open('crowdflower_results.json') as data_file:
        crowdflower_data = json.load(data_file)
    for crowdflower_result in crowdflower_data:
        for judgement in crowdflower_result['results']['judgments']:
            if judgement['unit_data']['title1'] == title1 and judgement['unit_data']['title2'] == title2:
                if judgement['data']['relevant'] == "Exact same event":
                    return True  
            elif judgement['unit_data']['title1'] == title2 and judgement['unit_data']['title2'] == title1:
                if judgement['data']['relevant'] == "Exact same event":
                    return True
    return False

@app.route('/')
def hello_world():
    return render_template('temp.html') 

@app.route('/search',  methods=['GET', 'POST'])
def search():
    query_string = request.form['search_input']
    results = search_query(query_string, solr_instance)
    return render_template('temp.html', results = results)
    
app.debug = True
app.jinja_env.filters['are_crowdflower_related'] = are_crowdflower_related
app.run()
