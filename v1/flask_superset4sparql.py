# flask_superset4sparql.py

# elasticsearch+http://192.168.3.133:5000
# http://192.168.3.49:5601/
# http://192.168.3.190:8890/sparql
# http://192.168.3.189:8088/superset/welcome/

'''
source venv/bin/activate
export FLASK_APP=flask_superset4virtuoso.py 
flask run --host=192.168.3.133 --debug
'''

# http://192.168.3.189:8088/superset/welcome/

import requests
import re

from flask import Flask
from flask import request

url = "http://192.168.3.190:7006/"
url = "http://192.168.3.190:8890/sparql"
url = "http://bio2rdf.org/sparql"

def create_alpha2() :
    alpha = []
    for a in range(97,123):
        l = chr(a)
        #print(a, l)
        alpha.append(l)

    alpha2 = []
    for l in alpha:
        alpha2.append(l)
        alpha2.append(l+str(1))
        alpha2.append(l+str(2))
        alpha2.append(l+str(3))
        alpha2.append(l+str(4))
        alpha2.append(l+str(5))
        alpha2.append(l+str(6))
        alpha2.append(l+str(7))
        alpha2.append(l+str(8))
        alpha2.append(l+str(9))
          
    return alpha2

#alpha2

def replace_identifier(query):
    
    alpha2 = create_alpha2()
    
    for l in alpha2:
        before = f' {l},'
        after = f' ?{l}'
        #print(l+'-'+before+'-'+after+'-')
        query = query.replace(before, after)
        before = f' {l} AS {l}'
        after = f' ?{l} '
        #print(l+'-'+before+'-'+after+'-')
        query = query.replace(before, after)
        before = f' {l} '
        after = f' ?{l} '
        #print(l+'-'+before+'-'+after+'-')
        query = query.replace(before, after)
        before = f'sum({l}) AS "SUM({l})"'
        after = f'(sum(?{l}) AS ?sum_{l})'
        #print(l+'-'+before+'-'+after+'-')
        query = query.replace(before, after)
        before = f'count({l}) AS "COUNT({l})"'
        after = f'(count(?{l}) AS ?count_{l})'
        #print(l+'-'+before+'-'+after+'-')
        query = query.replace(before, after)
        before = f'ORDER BY "COUNT({l})"'
        after = f'ORDER BY ?count_{l}'
        #print(l+'-'+before+'-'+after+'-')
        query = query.replace(before, after)

    return query



def sparql_show_columns(type_uri):
    sparql_query = {
        'query': 'select distinct ?p where { ?s ?p ?o . ?s a '+type_uri+' .}'
    }

    #url = "http://192.168.3.190:7006/"
    #url = "http://192.168.3.190:8890/sparql"
    
    sparql_query['format'] = 'json'
    response = requests.get(url, params=sparql_query)

    print(response.json())
    response_json = response.json()

    results_list = []
    for i in response_json['results']['bindings']:
        predicates = []
        predicate = i['p']['value']
        predicates.append('<'+predicate+'>')
        predicates.append('literal')
        predicates.append('text')
        if predicate.find('#x') != -1:
            predicates[1] = 'uri'
        results_list.append(predicates)

    columns_list = {}
    columns_list = {
        'columns':[{'name': 'column', 'type': 'keyword'}, 
                   {'name': 'type', 'type': 'keyword'}, 
                   {'name': 'mapping', 'type': 'keyword'}],
        'rows': results_list
    }
    
    print('columns_list',columns_list)
    return columns_list

#sparql_show_columns('<http://bio2rdf.org/bibtex#Article>')

def sparql_show_index():
    sparql_query = {
        'query': 'SELECT DISTINCT ?t WHERE { ?s a ?t .}'
    }

    #url = "http://192.168.3.190:7006/"
    #url = "http://192.168.3.190:8890/sparql"

    sparql_query['format'] = 'json'
    response = requests.get(url, params=sparql_query)

    #print(response.json())
    response_json = response.json()

    indexes = []
    for i in response_json['results']['bindings']:
        obj = {}
        obj['index'] = i['t']['value']
        indexes.append(obj)

    return indexes

#sparql_show_index()

def sparql2es_results(response):

    # create results table
    
    print('RESPONSE ', response) 
    
    head_list = response['head']['vars']

    results_list = response['results']['bindings']

    rows = []
    for row in results_list:
        row_dict = {}
        for key, value in row.items():
            val = value['value']
            if value['type'] in ['literal', 'typed-literal']:
                try:
                    if value['datatype'] == 'http://www.w3.org/2001/XMLSchema#integer':
                        val = int(val)
                    if value['datatype'] == 'http://www.w3.org/2001/XMLSchema#int':
                        val = int(val)
                        #print(val)
                    if value['datatype'] == 'http://www.w3.org/2001/XMLSchema#decimal':
                        val = float(val)
                except:
                    pass
            elif value['type'] == 'uri':
                val = '<' + value['value'] + '>'
                val = value['value']

            else:
                val = value['value']
                
            row_dict[key] = val
            
            #print(key, row_dict[key])

        new_row = []
        for col in head_list:
            #print(col, row_dict[col])
            new_row.append(row_dict[col])

        #print(new_row)
        rows.append(new_row)


    # create column name list with type

    first_row = response['results']['bindings'][0]

    print(first_row)
    
    column_names = []

    for col in head_list:
        #print(key, value['type'], value['value'])
        if first_row[col]['type'] in ['literal', 'typed-literal']:
            try:
                if first_row[col]['datatype'] == 'http://www.w3.org/2001/XMLSchema#integer':
                    type_name = "integer"
                if first_row[col]['datatype'] == 'http://www.w3.org/2001/XMLSchema#int':
                    type_name = "integer"
                if first_row[col]['datatype'] == 'http://www.w3.org/2001/XMLSchema#decimal':
                    type_name = "float"
            except:
                type_name = "text"
        else:
            type_name = "text"

        column  = {
            "name": col,
            "type": type_name
        }

        column_names.append(column)

    print(column_names)

    results = {
        "columns": column_names,
        "rows": rows
    }

    print(results)
    
    return results

app = Flask(__name__)

@app.post('/_sql')
def sql_query():
    content = request.get_json(silent=True)
    query = content['query'].replace('\n',' ')
    print('/_sql', query)
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
    print('QUERY_IN\n', query)

    query = query.replace('# PREFIX ','PREFIX ')


    query = query.replace('SELECT t AS t ','SELECT ?t ')
    query = query.replace('SELECT p AS p ','SELECT ?p ')
    query = query.replace(' ASC ',' ')
    query = query.replace(' DESC ',' ')
    
    #query = query.replace('SELECT c AS c,        p AS p,        t AS t ','SELECT ?c ?p ?t ')
    #query = query.replace('FROM   (','WHERE {')
    query = query.replace('FROM    (SELECT','WHERE {SELECT')
    query = query.replace('FROM   (SELECT','WHERE {SELECT')
    query = query.replace(') AS virtual_table','}')

    query = replace_identifier(query)
    
    '''
    query = query.replace(' c AS c',' c').replace(' c, ',' ?c ').replace(' c ',' ?c ')
    query = query.replace(' e AS e',' e').replace(' e, ',' ?e ').replace(' e ',' ?e ')
    query = query.replace(' f AS f',' f').replace(' f, ',' ?f ').replace(' f ',' ?f ')
    query = query.replace(' g AS g',' g').replace(' g, ',' ?g ').replace(' g ',' ?g ')
    query = query.replace(' m AS m',' m').replace(' m, ',' ?m ').replace(' m ',' ?m ')
    query = query.replace(' t AS t',' t').replace(' t, ',' ?t ').replace(' t ',' ?t ')
    '''
    
    
    query = query.replace('count(*) AS count', '(count(*) AS ?count)')
    query = query.replace('ORDER BY count', 'ORDER BY ?count')
        
    query = query.replace('count(DISTINCT s1) AS "COUNT_DISTINCT(s1)"', '(count(DISTINCT ?s1) AS ?COUNT_DISTINCT_s1)')
    query = query.replace('count(DISTINCT s2) AS "COUNT_DISTINCT(s2)"', '(count(DISTINCT ?s2) AS ?COUNT_DISTINCT_s2)')
    query = query.replace('count(DISTINCT s3) AS "COUNT_DISTINCT(s3)"', '(count(DISTINCT ?s3) AS ?COUNT_DISTINCT_s3)')

    query = query.replace('SELECT COUNT(*) AS "COUNT(*)" ', 'SELECT (count(*) AS ?count) ')
    #query = query.replace('SELECT count(m) AS "COUNT(m)"', 'SELECT (count(?m) AS ?count)')
    #query = query.replace('SELECT count(g) AS "COUNT(g)"', 'SELECT (count(?g) AS ?count)')
    #query = query.replace('count(c) AS "COUNT(c)"', '(count(?c) AS ?zCOUNT_c)')
    query = query.replace('ORDER BY "COUNT(c)"', 'ORDER BY ?zCOUNT_c')

    #query = query.replace('sum(c) AS "SUM(c)"',' (sum(?c) AS ?zSUM_c) ')
    #query = query.replace('"SUM(c)"','?zSUM_c')
    query = query.replace('WHERE {SELECT ?t','WHERE {{SELECT ?t')
    
    query = query.replace('GROUP BY ?t ?p}','GROUP BY ?t ?p}}')
    #query = query.replace('LIMIT 1000','} LIMIT 1000')
    query = query.replace('ORDER BY ?t }} LIMIT', 'ORDER BY ?t LIMIT')
    
    query = query.replace('SELECT ?m        count(*) AS count','SELECT ?m (count(?m) as ?count)')
    query = query.replace('SELECT ?g        count(*) AS count','SELECT ?g (count(?g) as ?count)')
    query = query.replace('ORDER BY count','ORDER BY ?count')
    
    
    # create sparql filter
    if query.find('IN (') != -1:
        print('###IN', query)
        
        match = re.match('.*(WHERE (.*) GROUP).*', query)
        if match:
            print('###IN WHERE-GROUP', query)
            filter_in = match.group(1)
            filter_out = filter_in
            print('FILTER_IN', filter_in)
            filter_out = filter_out.replace('WHERE ',' FILTER(')
            filter_out = filter_out.replace(') GROUP','))} GROUP')
            print('FILTER_OUT', filter_out)
            query = query.replace(filter_in, filter_out)

            query = query.replace("WHERE {select",'WHERE {{SELECT')
            query = query.replace("WHERE {SELECT",'WHERE {{SELECT')
        
        else:
            match = re.match('.*(} WHERE (.*) LIMIT).*', query)
            if match:
                print('###IN WHERE-LIMIT', query)
                filter_in = match.group(1)
                filter_out = filter_in
                print('FILTER_IN', filter_in)
                filter_out = filter_out.replace('WHERE ',' FILTER(')
                filter_out = filter_out.replace('LIMIT',')} LIMIT')
                print('FILTER_OUT', filter_out)
                query = query.replace(filter_in, filter_out)
                query = query.replace("WHERE {select",'WHERE {{SELECT')
                query = query.replace("WHERE {SELECT",'WHERE {{SELECT')
        

    query = query.replace('}} FILTER','} FILTER')
        
        
    content['query'] = query    
    
    print('QUERY_OUT\n', content['query'])
    
    if content['query'] == 'SHOW TABLES':
        #url = 'http://es.kibio.science/_sql?format=json'
        #response = requests.post(url, json=content)
        #response_json = response.json()
        
        show_tables = {'columns': [{'name': 'catalog', 'type': 'keyword'}, {'name': 'name', 'type': 'keyword'}, {'name': 'type', 'type': 'keyword'}, {'name': 'kind', 'type': 'keyword'}], 'rows': [['es1-v8-kibio-prod', 'ztest', 'TABLE', 'INDEX']]}
      
        print('SHOW TABLES', show_tables)
        
        response_show_tables = []
        for index_table in sparql_show_index():
            #print(index_table['index'])
            response_show_tables.append(['sparql_endpoint', '<'+index_table['index']+'>', 'TABLE', 'INDEX'])
        
        show_tables['rows'] = response_show_tables
        response_json = show_tables
        
    elif content['query'][0:12] == 'SHOW COLUMNS':
        table_uri = content['query'][19:-1]
        print('SHOW COLUMNS', table_uri)

        response_json = sparql_show_columns(table_uri)

        print('SHOW COLUMNS', response_json)
        
    elif content['query'].find('WHERE') == -1 and content['query'].find('LIMIT 101') != -1:
        print('DISPLAY')
        
        query = content['query']
        extract_from = query[query.find(' FROM "')+7:-11]
        print(extract_from)
        
        content['query'] = '''
        select ?subject ?predicate ?object
        where {
            ?subject ?predicate ?object .
            ?subject a <TYPE> .
        } 
        LIMIT 1001
        '''

        
        content['query'] = content['query'].replace('<TYPE>',extract_from)


        #url = "http://192.168.3.190:7006/"
        #url = "http://192.168.3.190:8890/sparql"

        content['format'] = 'json'
        print(content)
        response = requests.get(url, params=content)
        response_json = sparql2es_results(response.json())

    else:     
        #url = "http://192.168.3.190:7006/"
        #url = "http://192.168.3.190:8890/sparql"
        print("URL", url)


        print("ELSE", content)
        content['format'] = 'json'
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
    
    #print('CAT', response_json)

    response_index = []
    for cat_index in sparql_show_index():
        #print(cat_index['index'])
        index_def = {'health': 'green', 'status': 'open', 'index': cat_index['index'], 'uuid': 'GWM6lcf0Rtydyfokup6Pww', 'pri': '1', 'rep': '1', 'docs.count': '1', 'docs.deleted': '0', 'store.size': '1kb', 'pri.store.size': '1kb'}
        response_index.append(index_def)
    #print(response_index)
    
    return response_index

@app.get('/')
def home():
    url = "http://es.kibio.science/"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    response_json = response.json()
    #print(response_json)

    return response_json

#@app.route('/http%3A%2F%2Fbio2rdf.org%2Fbibtex%23Article/_search', methods=['POST'])
@app.route('/<path:index_name>/_search', methods=['POST'])
def post_home(index_name):
    print('POST SEARCH', index_name)
    
    url = "http://es.kibio.science/entrez_gene_v2/_search?size=1"
    response = requests.post(url)
    response_json = response.json()
    
    #print(response_json)

    return response_json
