import json
import boto3
import botocore
from datetime import datetime
from aws_requests_auth.aws_auth import AWSRequestsAuth
import requests
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import os

def appLambda(event, context):
    connectionID = event["requestContext"]["connectionID"]
    body = json.loads(event["body"])
    ReceiverID = body["ReceiverID"]
    Msg = body["Msg"]
    MessageDateTime = str(datetime.now().timestamp())
    dynamoConnections = boto3.resource('dynamodb').Table("connectionTable")
    resultU = dynamoConnections.scan(FilterExpression = Key('UserID').eq(ReceiverID))
    if resultU["Items"] is not None and len(resultU["Items"]) == 1:
        ReceiverConnectionID = resultU["Items"][0]["token"]
        reultX = dynamoConnections.scan(FilterExpression = Key("token").eq(connectionID))
        if resultX["Items"] is not None and len(resultX["Items"]) == 1:
            SenderID = resultX["Items"][0]["UserID"]
            jsonObjToSend = {"MessageID": MessageDateTime, "Message": Msg, "SenderID": SenderID}
            sendDirectMessage(ReceiverConnectionID, jsonObjToSend)
            return {"statusCode": 200, "body" : "Message delivered"}
        else:
            return {"statusCode": 200, "body" : "Error Occured"}
    else:
        return {"statusCode": 200, "body" : "User offline"}

def sendDirectMessage(token, jsonobj):
    access_key = os.environ['access_key']
    secret_key = os.environ['secret_key']
    auth = AWSRequestsAuth(aws_access_key = access_key,
    aws_secret_access_key = secret_key,
    aws_host = '  https://fxon08vym0.execute-api.us-east-1.amazonaws.com', 
    aws_region = 'us-east-1',
    aws_service = 'execute-api')
    url = 'https://fxon08vym0.execute-api.us-east-1.amazonaws.com/dev/%40connections' + token.replace("=","") + "%3D"
    req = requests.post(url, auth = auth, data = str(jsonobj))
    print(req.text)

    