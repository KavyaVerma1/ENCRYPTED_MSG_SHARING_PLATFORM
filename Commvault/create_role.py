import boto3
import json

client = boto3.client('iam')

   
role_name = 'db access'
assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

try:
    response = client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
        )
    print(f"Role '{role_name}' created successfully: {response['Role']['Arn']}")
except client.exceptions.EntityAlreadyExistsException:
        print(f"Role '{role_name}' already exists.")
except Exception as e:
        print(f"Error creating role: {e}")

    
policy_arn='arn:aws:iam::aws:policy/job-function/DatabaseAdministrator'



    
db_access_policy={
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudwatch:DeleteAlarms",
                "cloudwatch:Describe*",
                "cloudwatch:DisableAlarmActions",
                "cloudwatch:EnableAlarmActions",
                "cloudwatch:Get*",
                "cloudwatch:List*",
                "cloudwatch:PutMetricAlarm",
                "datapipeline:ActivatePipeline",
                "datapipeline:CreatePipeline",
                "datapipeline:DeletePipeline",
                "datapipeline:DescribeObjects",
                "datapipeline:DescribePipelines",
                "datapipeline:GetPipelineDefinition",
                "datapipeline:ListPipelines",
                "datapipeline:PutPipelineDefinition",
                "datapipeline:QueryObjects",
                "dynamodb:*",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeAddresses",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeVpcs",
                "elasticache:*",
                "iam:ListRoles",
                "iam:GetRole",
                "kms:ListKeys",
                "lambda:CreateEventSourceMapping",
                "lambda:CreateFunction",
                "lambda:DeleteEventSourceMapping",
                "lambda:DeleteFunction",
                "lambda:GetFunctionConfiguration",
                "lambda:ListEventSourceMappings",
                "lambda:ListFunctions",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:FilterLogEvents",
                "logs:GetLogEvents",
                "logs:Create*",
                "logs:PutLogEvents",
                "logs:PutMetricFilter",
                "rds:*",
                "redshift:*",
                "s3:CreateBucket",
                "sns:CreateTopic",
                "sns:DeleteTopic",
                "sns:Get*",
                "sns:List*",
                "sns:SetTopicAttributes",
                "sns:Subscribe",
                "sns:Unsubscribe"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:AbortMultipartUpload",
                "s3:DeleteObject*",
                "s3:Get*",
                "s3:List*",
                "s3:PutAccelerateConfiguration",
                "s3:PutBucketTagging",
                "s3:PutBucketVersioning",
                "s3:PutBucketWebsite",
                "s3:PutLifecycleConfiguration",
                "s3:PutReplicationConfiguration",
                "s3:PutObject*",
                "s3:Replicate*",
                "s3:RestoreObject"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "arn:aws:iam::*:role/rds-monitoring-role",
                "arn:aws:iam::*:role/rdbms-lambda-access",
                "arn:aws:iam::*:role/lambda_exec_role",
                "arn:aws:iam::*:role/lambda-dynamodb-*",
                "arn:aws:iam::*:role/lambda-vpc-execution-role",
                "arn:aws:iam::*:role/DataPipelineDefaultRole",
                "arn:aws:iam::*:role/DataPipelineDefaultResourceRole"
            ]
        }
    ]
}
try:
        client.put_role_policy(
            RoleName=role_name,
            PolicyName='CustomRDSConnect',
            PolicyDocument=json.dumps(db_access_policy)
        )
        print("Custom inline policy attached successfully.")
except Exception as e:
        print(f"Error attaching inline policy: {e}")