import os
import base64
import hmac
import hashlib
import datetime
import time

from dotenv import load_dotenv
load_dotenv()

import requests

import boto3
from botocore.config import Config

BASE_URL = "https://api.kucoin.com"

API_KEY = os.getenv('KUCOIN_API_KEY')
api_secret = os.getenv('KUCOIN_API_SECRET')
api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')

endpoints = {
    "GET_ACCOUNT": "/api/v1/accounts",
    "TIMESTAMP": "/api/v1/timestamp"
}

#Returns -- AWS boto3 client

def connect_to_aws():
    aws_config = Config(
        region_name = 'us-east-1',
        signature_version = 'v4',
    )

    dynamo = boto3.client('dynamodb',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        config=aws_config)

    return dynamo

def load_data(table='fleshel-kucoin'):
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'GET' + '/api/v1/accounts'

    signature = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), 'sha256').digest())

    passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), 'sha256').digest())

    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": API_KEY,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }

    response = requests.request('get', BASE_URL+endpoints['GET_ACCOUNT'], headers=headers)

    print('request completed with status code={sc}'.format(sc=response.status_code))

    response_data = response.json()['data'] if response.json()['code'] == '200000' else []

    print('fetched data for {n} accounts'.format(n=len(response_data)), end='\n\n')

    balances = {}
    accounts = {}
    skipped_accts = 0

    for a in range(len(response_data)):
        #   print('account: {act}'.format(act=account))
        account = response_data[a]
        
        print(account)

        accounts[account['id']] = account['balance']

        curr = account['currency']
        balance = account['balance']

        if curr in balances.keys():
            balances[curr] += balance
        else:
            balances[curr] = balance


        if float(balance) > 0:
            print('[account {n} |{type}] bal: {bal} / {avl} avail ({cxy})'.format(
                n=a+1,
                type=account['type'].upper(),
                bal=account['balance'],
                avl=account['available'],
                cxy=account['currency']),
                end='\n\n'
            )
        else:
            skipped_accts += 1

    if skipped_accts > 0:
        print('\nSkipped {n} emtpy accounts.'.format(n=skipped_accts),end='\n\n')
    print('BALANCE SUMMARY:')

    hidden_bals = 0
    for k in balances.keys():
        balance = balances[k]
        if float(balance) > 0:
            print('{cxy}: {bal}'.format(cxy=k, bal=balances[k]))
        else:
            hidden_bals += 1
        
    print('\nSkipped {n} empty coins'.format(n=hidden_bals))

    dynamo = connect_to_aws()

    print(accounts)
    record = {
        "date": {
            'S': str(datetime.datetime.now()), #   TODO: change to now with time?
        }
    }
    for account in accounts:
        record[account] = {
            'N': str(accounts[account])
        }

    dynamo.put_item(TableName=table, Item=record)

load_data()