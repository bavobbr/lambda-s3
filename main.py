# main.py
import io
import logging
import os
import time
from urllib.parse import urlparse

import boto3
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Flask
from flask import request

load_dotenv()
bucketname = os.getenv("BUCKET")
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello boto"


@app.route("/store", methods=['POST'])
def store():
    myfile = request.form.get('location')
    print('Original location is: {}'.format(myfile))
    response = requests.get(myfile)
    parsedpurl = urlparse(myfile)
    split_tup = os.path.splitext(parsedpurl.path)
    file_extension = split_tup[1]
    timestr = time.strftime("%Y%m%d-%H%M%S")
    fname = timestr + file_extension
    print('Uploading file {}'.format(fname))
    bytedata = io.BytesIO(response.content)
    uploaded = upload_file(bytedata, bucketname, fname)
    print(uploaded)
    return uploaded


def upload_file(file_data, bucket, object_name):
    # usession = boto3.Session(profile_name="zappa")
    usession = boto3.Session()
    s3_client = usession.client('s3')
    try:
        s3_client.upload_fileobj(file_data, bucket, object_name)
        url = "https://%s.s3.amazonaws.com/%s" % (bucket, object_name)
        print(url)
    except ClientError as e:
        logging.error(e)
        return None
    return url
