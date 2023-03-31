# flask_superset4sparql

# elasticsearch+http://192.168.3.133:5000

# source venv/bin/activate
# export FLASK_APP=prog_lang_app.py
# flask run --host=192.168.3.133 --debug

# http://192.168.3.189:8088/superset/welcome/

import requests

from flask import Flask
from flask import request

def sparql2es_results(response):

    # create results table
    
    results = response['results']['bindings']

    rows = []

    for row in results:
        #print(row)
        columns = []
        for key, value in row.items():
            #print(key, value['type'], value['value'])
            val = value['value']
            if value['type'] == 'literal':
                if value['datatype'] == 'http://www.w3.org/2001/XMLSchema#int':
                    val = int(val)
                if value['datatype'] == 'http://www.w3.org/2001/XMLSchema#decimal':
                    val = float(val)

            #print(key, val, type(val))
            columns.append(val)

        rows.append(columns)

    # create column name list with type

    first_row = response['results']['bindings'][0]

    column_names = []

    for key, value in first_row.items():
        #print(key, value['type'], value['value'])
        if value['type'] == 'literal':
            if value['datatype'] == 'http://www.w3.org/2001/XMLSchema#int':
                type_name = "integer"
            if value['datatype'] == 'http://www.w3.org/2001/XMLSchema#decimal':
                type_name = "float"
        else:
            type_name = "text"

        column  = {
            "name": key,
            "type": type_name
        }

        column_names.append(column)

    column_names

    results = {
        "columns": column_names,
        "rows": rows
    }

    return results

app = Flask(__name__)

@app.post('/_sql')
def sql_query():
    return {"columns":[{"name":"1","type":"integer"}],"rows":[[1]]}

@app.post('/_sql2/')
def sql_query2es():
    content = request.get_json(silent=True)
    print(content)

    url = "http://es.kibio.science/_sql?format=json"

    response = requests.post(url, json=content)
    
    response_json = response.json()
    #print(response_json)
    
    return response_json
    
@app.post('/_sql/')
def sql_query2sparql():
    content = request.get_json(silent=True)
    query = content['query'].replace('\n',' ')
    print('QUERY_IN', query)


    query = query.replace('SELECT t AS t ','SELECT ?t ')
    query = query.replace('SELECT p AS p ','SELECT ?p ')
    query = query.replace(' ASC ',' ')
    query = query.replace(' DESC ',' ')
    
    #query = query.replace('SELECT c AS c,        p AS p,        t AS t ','SELECT ?c ?p ?t ')
    query = query.replace('FROM   (select','WHERE {select').replace(') AS virtual_table','}')
     
    query = query.replace(' c AS c',' c').replace(' p AS p',' p').replace(' t AS t',' t')
    query = query.replace(' c, ',' ?c ').replace(' p, ',' ?p ').replace(' t, ',' ?t ')
    query = query.replace(' c ',' ?c ').replace(' p ',' ?p ').replace(' t ',' ?t ')

    query = query.replace('sum(c) AS "SUM(c)"',' (sum(?c) AS ?zSUM_c) ')
    query = query.replace('"SUM(c)"','?zSUM_c')
    
    
    
    if query.find('IN (') != -1:
        query = query.replace("WHERE ?p IN ('http://xmlns.com/foaf/0.1/name')",'FILTER(?p  = <http://xmlns.com/foaf/0.1/name>)}')
        query = query.replace("WHERE ?t IN ('http://bio2rdf.org/bibtex#Article')",'FILTER(?t  = <http://bio2rdf.org/bibtex#Article>)}')
        query = query.replace("WHERE {select",'WHERE {{select')

    content['query'] = query    
    
    print('QUERY_OUT', content['query'])

    if content['query'][0:4] == 'SHOW':
        url = 'http://es.kibio.science/_sql?format=json'

        response = requests.post(url, json=content)

        response_json = response.json()
        #print(response_json)
        
    else:     
        url = "http://192.168.3.190:7006/"

        response = requests.get(url, params=content)

        #print(response.json())
        response_json = sparql2es_results(response.json())
        #print(response_json)
    
    return response_json

@app.get('/_cat/indices')
def cat_indices():
    url = "http://es.kibio.science/_cat/indices?format=json"
    response = requests.get(url)
    response_json = response.json()

    return response_json

@app.get('/')
def home():
    url = "http://es.kibio.science/"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    response_json = response.json()
    #print(response_json)

    return response_json

@app.route('/<string:index_name>/_search', methods=['POST'])
def post_home(index_name):
    url = "http://es.kibio.science/"+index_name+"/_search?size=1"
    response = requests.post(url)
    response_json = response.json()
    
    #print(response_json)

    return response_json
