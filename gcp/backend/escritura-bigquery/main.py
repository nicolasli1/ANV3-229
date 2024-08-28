import functions_framework
from google.cloud import bigquery

@functions_framework.http
def hello_http(request):
    client = bigquery.Client()
    table_id="grounded-primer-436816-b5.DatasetCurso.Estudiantes-curso"

    body_json = request.get_json()

    id = body_json["id"]
    name = body_json["name"]

    rows_to_insert=[{
        "id":id,
        "Nombre":name
    }

    ]
    errors = client.insert_rows_json(table_id, rows_to_insert) 
    if errors == []:
        return f'Data insertada', 200
    else:
        return f'Data No insertada', 500

 
    