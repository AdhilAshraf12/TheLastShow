terraform {
  required_providers {
    aws = {
      version = ">= 4.0.0"
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
  access_key = "AKIAUWE7CGSAQMBMAAOQ"
  secret_key = "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"
}

// DynamoDB table creator.
resource "aws_dynamodb_table" "image_table" {
  name         = "image_table"
  billing_mode = "PROVISIONED"
  hash_key     = "image_id"
  read_capacity = 1
  write_capacity = 1
  attribute {
    name = "image_id"
    type = "S"
  }
}


resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow",
        Sid = ""
      }
    ]
  })
}



// Function creator for "create-obituary"
resource "aws_lambda_function" "create-obituary-30140009" {
  filename      = "create-obituary-30140009.zip"
  function_name = "create-obituary-30140009"
  role          = aws_iam_role.lambda_role.arn
  handler       = "create-obituary-30140009.lambda_handler"
  runtime       = "python3.8"
  timeout       = 180
  
}


resource "aws_lambda_function" "get-obituaries-30123167" {
  filename      = "get-obituaries-30123167.zip"
  function_name = "get-obituaries-30123167"
  role          = aws_iam_role.lambda_role.arn
  handler       = "get-obituaries-30123167.lambda_handler"
  runtime       = "python3.8"
  timeout       = 180
  
}


resource "aws_lambda_function_url" "create-obituary-30140009-url" {
  function_name = aws_lambda_function.create-obituary-30140009.function_name
  authorization_type = "NONE"
  

  cors{
    allow_credentials = true
    allow_origins = ["*"]
    allow_methods = ["POST"]
    allow_headers     = ["*"]
    expose_headers = ["keep-alive","date"]
  }
}


resource "aws_lambda_function_url" "get-obituaries-30123167-url" {
  function_name = aws_lambda_function.get-obituaries-30123167.function_name
  authorization_type = "NONE"
  

  cors{
    allow_credentials = true
    allow_origins = ["*"]
    allow_methods = ["GET"]
    allow_headers     = ["*"]
    expose_headers = ["keep-alive","date"]
  }
}

data "archive_file" "create-obituary-30140009" {
  type        = "zip"
  source_dir  = "../functions/create-obituary"
  output_path = "create-obituary-30140009.zip"
}

data "archive_file" "get-obituaries-30123167" {
  type        = "zip"
  source_file  = "../functions/get-obituaries/main.py"
  output_path = "get-obituaries-30123167.zip"
}

// Gives permissions to the functions to do the things they need to do.
resource "aws_iam_policy" "logs" {
  name        = "lambda-logging-create-obituary-30140009"
  description = "IAM policy for logging from Lambda function create-obituary-30140009"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = "arn:aws:logs:::*"
        Effect   = "Allow"
      },
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan",
        ]
        Resource = aws_dynamodb_table.image_table.arn
        Effect   = "Allow"
      },
      {
        Action = [
          "ssm:GetParametersByPath",
        ]
        Resource = "*"
        Effect   = "Allow"
      },
      {
        Action = [
          "polly:SynthesizeSpeech",
        ]
        Resource = "*"
        Effect   = "Allow"
      },
    ]
  })
}


output "create_obituary_url"{
  value = aws_lambda_function_url.create-obituary-30140009-url.function_url
  description = "This is the create-obituary URL."
}
output "get_obituary_url"{
  value = aws_lambda_function_url.get-obituaries-30123167-url.function_url
  description = "This is the get-obituaries URL."
}

resource "aws_iam_role_policy_attachment" "lambda_logs_attachment" {
  policy_arn = aws_iam_policy.logs.arn
  role       = aws_iam_role.lambda_role.name
}