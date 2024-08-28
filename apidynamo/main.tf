
#construccion de las lambdas
resource "aws_lambda_function" "fn_get_items_table" {
  function_name = "Fn_get_items_table"
  handler       = "lambda_get_items_code.lambda_handler"
  runtime       = "python3.10"
  timeout       = 60
  filename      = "../lambda/Fn_api_dynamo/lambda_get_items_code.zip"
  role          = aws_iam_role.lambda_exec_role.arn
}

resource "aws_lambda_function" "fn_post_items_table" {
  function_name = "Fn_post_items_table"
  handler       = "lambda_post_items_code.lambda_handler"
  runtime       = "python3.10"
  timeout       = 60
  filename      = "../lambda/Fn_api_dynamo/lambda_post_items_code.zip"
  role          = aws_iam_role.lambda_exec_role.arn
}

#construccion de la base de datos en dynamo

resource "aws_dynamodb_table" "global_table" {
  name         = "My_primera_global_table_292"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "id_pk"
    type = "S"
  }

  hash_key = "id_pk"

  lifecycle {
    prevent_destroy = false
  }
}

# creacion de los roles y politicas

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [{
      "Action" : "sts:AssumeRole",
      "Principal" : {
        "Service" : "lambda.amazonaws.com"
      },
      "Effect" : "Allow"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:*"
        ],
        "Resource" : aws_dynamodb_table.global_table.arn
      }
    ]
  })
}

# creacion del api gateway

resource "aws_api_gateway_rest_api" "MyDemoAPI" {
  name        = "MyDemoAPI"
  description = "This is my API for demonstration purposes"
}

resource "aws_api_gateway_resource" "MyDemoResource" {
  rest_api_id = aws_api_gateway_rest_api.MyDemoAPI.id
  parent_id   = aws_api_gateway_rest_api.MyDemoAPI.root_resource_id
  path_part   = "items"
}

resource "aws_api_gateway_method" "get_items" {
  rest_api_id   = aws_api_gateway_rest_api.MyDemoAPI.id
  resource_id   = aws_api_gateway_resource.MyDemoResource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "post_items" {
  rest_api_id   = aws_api_gateway_rest_api.MyDemoAPI.id
  resource_id   = aws_api_gateway_resource.MyDemoResource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_items_integration" {
  rest_api_id             = aws_api_gateway_rest_api.MyDemoAPI.id
  resource_id             = aws_api_gateway_resource.MyDemoResource.id
  http_method             = aws_api_gateway_method.get_items.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fn_get_items_table.invoke_arn
}

resource "aws_api_gateway_integration" "post_items_integration" {
  rest_api_id             = aws_api_gateway_rest_api.MyDemoAPI.id
  resource_id             = aws_api_gateway_resource.MyDemoResource.id
  http_method             = aws_api_gateway_method.post_items.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fn_post_items_table.invoke_arn
}

# Permisos de Invocación para API Gateway

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fn_get_items_table.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.MyDemoAPI.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_post" {
  statement_id  = "AllowAPIGatewayInvokePost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fn_post_items_table.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.MyDemoAPI.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "MyDemoAPI_deployment" {
  rest_api_id = aws_api_gateway_rest_api.MyDemoAPI.id
  depends_on = [
    aws_api_gateway_integration.get_items_integration,
    aws_api_gateway_integration.post_items_integration,
  ]
}

# Creacion del stage para el endpoint

resource "aws_api_gateway_stage" "MyDemoAPI_stage" {
  stage_name    = "prod"
  rest_api_id   = aws_api_gateway_rest_api.MyDemoAPI.id
  deployment_id = aws_api_gateway_deployment.MyDemoAPI_deployment.id
}


# curl -X POST https://8wygp2xlkl.execute-api.us-east-1.amazonaws.com/prod/items \                       
# -H "Content-Type: application/json" \
# -d '{"id_pk": "1", "key1": "101", "key2": "Manny"}'