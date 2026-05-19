import os
import sys
import boto3
import zipfile
import json

# 1. SETUP PATH AND BUCKET CONFIG
LIB_PATH = "/tmp/python"
BUCKET_NAME = 'cloud-sentry-ml-model-abhishek'
MODEL_FILE = 'alarm_model.joblib'
LOCAL_MODEL_PATH = '/tmp/model.joblib'

# 2. RUN EXTRACTION AT INIT
if not os.path.exists(LIB_PATH):
    print("Downloading libraries from S3...")
    s3 = boto3.client('s3')
    s3.download_file(BUCKET_NAME, 'ml_libs.zip', '/tmp/ml_libs.zip')

    with zipfile.ZipFile('/tmp/ml_libs.zip', 'r') as zip_ref:
        zip_ref.extractall('/tmp/')
    print("Extraction complete.")

# 3. UPDATE SYSTEM PATH
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

# 4. NOW IMPORT ML MODULES (Scoped here to prevent early import errors)
import joblib
import sklearn
import scipy
import pandas as pd

# Initialize the S3 client for the handler
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    try:
        # 1. Download model if not present
        if not os.path.exists(LOCAL_MODEL_PATH):
            print(f"Downloading model from {BUCKET_NAME}...")
            s3_client.download_file(BUCKET_NAME, MODEL_FILE, LOCAL_MODEL_PATH)

        # 2. Load the model
        model = joblib.load(LOCAL_MODEL_PATH)

        # 3. Parse input
        body = json.loads(event.get('body', '{}'))

        # Extract features
        duration = body.get('duration')
        severity = body.get('severity')
        frequency = body.get('frequency')

        # 4. Predict
        data_point = [[duration, severity, frequency]]
        prediction = model.predict(data_point)
        result = "False Alarm" if prediction[0] == -1 else "Normal"

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'prediction': result,
                'input_received': body
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }