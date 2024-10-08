import functions_framework
from google.cloud import bigquery

@functions_framework.http
def hello_http(request):
    client = bigquery.Client()

    query = f'SELECT * FROM `grounded-primer-436816-b5.DatasetCurso.Estudiantes-curso` LIMIT 1000'

    results = client.query(query).result() 

    rows = [dict(row) for row in results]
    
    return {'data': rows}, 200
