import json
from article import Article
import operator
from textblob import TextBlob
import solr


NUM_TOP_ARTICLES = 15
THREASHOLD_VALUE = 6

def get_top(sentence, n):
    '''
    Get the top n most frequently used nouns in a string
    @param sentence: The string being analyzed
    @param n: The number of results desired
    @return: An array of n nouns sorted by frequency of use in sentence in descending order
    '''
    blob = TextBlob(sentence)
    most_used_nps = blob.np_counts
    sorted_nps = sorted(most_used_nps.items(), key=operator.itemgetter(1), reverse=True)
    i = 0
    arr = []
    for entry in sorted_nps:
        if(i < n):
            arr.append(entry[0])
    return arr

def are_similar_top(top_a, top_b, threshold):
    '''
    Determines whether two lists of frequently used nouns have at least threashold nouns in common
    @param top_a: A list of nouns
    @param top_b: A list of nouns
    @param threshold: How many nouns top_a and top_b must have in common in order to be similar
    @return True if top_a and top_b have threshold nouns in common, False otherwise
    '''
    num_same = 0
    for term in top_a:
        if term in top_b:
            num_same += 1
    return num_same >= threshold

def are_similar(text_1, text_2, n, threshold):
    '''
    Determines if two strings are similar given than they share threshold nouns in their 
    top n most frequently used nouns
    @param text_1: A string
    @param text_2: A string  
    @param n: How many of the most frequently used nouns in each string should be considered
    @param threshold: How many frequently used nouns the strings must have in common to be similar
    @return: True if text_1 and text_2 have threshold nouns in common between their top n most frequently 
    used words, False otherwise
    '''
    top_1 = get_top(text_1, n)
    top_2= get_top(text_2, n)
    return are_similar_top(top_1, top_2, threshold)

def cluster(article_arr):
    '''
    Compares all the articles to ensure that each related article has the same parent_id
    @param article_arr: a list of articles
    '''
    #i is the article who's parent_id is being set
    for i in range(1, len(article_arr)): 
        #j is the article who is being compared to article i for similarity
        for j in range(0, i):
            # If articles i and j have 6 nouns in common in their top 15 most frequently used nouns 
            if are_similar(article_arr[i].content, article_arr[j].content, NUM_TOP_ARTICLES, THREASHOLD_VALUE):
                # If prevents self assignment
                if article_arr[i].id != article_arr[j].id:
                    # This is OK because root articles are their own parent
                    article_arr[i].parent_id = article_arr[j].parent_id
                    
def get_article_by_id(json_data, _id):
    '''
    Gets an article from article.json by id
    @param json_data: The array of articles in json format
    @param _id: The article id you want to get from json_dat
    @return: The json data of the article with id _id
    '''
    for i in range(len(json_data)):
        if int(json_data[i]["id"]) == _id:
            return json_data[i]
    return None

def update_parent_by_id(article_id, parent_id, json_data, solr_instance):
    '''
    Updates the parent_id of an article in solr
    @param article_id: The id of the article to update
    @param parent_id: The parent_id the article should have
    @param json_data: The array of articles in json format
    @param solr_instance: The solr instance which is being updated 
    '''
    solr_instance.delete(id = str(article_id))
                    
    article_data = get_article_by_id(json_data, article_id)
    solr_instance.add(id = article_data['id'], title = article_data['title'], content = article_data['content'], url = article_data['url'], organization = article_data['organization'], parent_id = str(parent_id))

    solr_instance.commit()
    
def update_parents_util(article_arr, json_data, solr_instance):
    '''
    Update the parent_ids of every article in article_arr on solr so that similar articles 
    have the same parent_id
    @param article_arr: An array of article objects 
    @param json_data: An array of articles in json_format
    @param solr_instance: The solr instance which is being updated 
    '''
    cluster(article_arr)
    for article in article_arr:
        update_parent_by_id(article.id, article.parent_id, json_data, solr_instance)

def update_parents(solr_instance):
    '''
    Updates solr so that every related article in articles.json has the same parent_id field
    @param solr_instance: The solr instance which is being updated  
    '''
    with open('articles.json') as data_file:
        json_data = json.load(data_file)
    article_arr = []
    for i in range(len(json_data)):
        article_id = int(json_data[i]["id"])
        article_content = json_data[i]["content"]
        article_arr.append(Article(article_id, article_content))       
    update_parents_util(article_arr, json_data, solr_instance)
    
def get_similar_articles(_id, solr_instance):
    '''
    Get the articles similar to the article with the id _id
    @param _id: (int) Id of the article to get similar articles for
    @param solr_instance: The solr instance that is being queried
    @return: An array of json articles that are related to _id excluding itself  
    '''
    parent_id = solr_instance.query('id:' + str(_id)).results[0].get('parent_id', -1)
    related_articles = solr_instance.query('parent_id:' + str(parent_id[0])).results
    result = []
    # the excluding itself code is below
    for article in related_articles:
        if _id != int(article['id']):
            result.append(article)
    return result

def search_query(query_string, solr_instance):
    return solr_instance.query(query_string).results

solr_instance = solr.SolrConnection('http://localhost:8983/solr/gettingstarted')
update_parents(solr_instance)

#test code
'''
response = solr_instance.query('id:1')
print response.results
for hit in response.results:
    print hit.get('title', "shoe through")[0]
    print hit.get('parent_id', "no parent")[0] == 1

response = solr_instance.query('id:2')
for hit in response.results:
    print hit.get('title', "shoe through")[0]
    print hit.get('parent_id', "no parent")[0] == 1
    
response = solr_instance.query('id:3')
for hit in response.results:
    print hit.get('title', "shoe through")[0]
    print hit.get('parent_id', "no parent")[0] == 3
    

print len(get_similar_articles(3, solr_instance)) == 0
print len(get_similar_articles(1, solr_instance)) == 1 
'''  
#response = solr_instance.query('id:1')
#for hit in response.results:
#    print hit.get('title', "shoe through")
#    print hit.get('parent_id', "no parent")[0]
#print are_similar(text_1, text_2, 10, 2)
#get queries from front end
#get RESULTS
#get related articles to those RESULTS
#populate frontend with results and their associated related articles.
#readme