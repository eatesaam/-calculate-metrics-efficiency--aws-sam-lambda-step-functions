import boto3
import json
import os
import pymysql
import base64
import json
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "starkey-technologies-safe-metrics-db"
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    print("Client created")

    try:
        print("Getting secret")
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except:
        print("Got an error")
    else:
        print("Got the secret")
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            print("Secret is a string")
            return json.loads(secret)
        else:
            print("Is a binary")
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])

            return json.loads(str(decoded_binary_secret))


def lambda_handler(event, context):

    data = []

    print("Getting secret")
    secret_content = get_secret()

    print("Got the secret")
    

    host = secret_content.get("host")
    db_name = secret_content.get("dbname")
    user = secret_content.get("username")
    password = secret_content.get("password")

    try:
        print("Connecting to database")
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database="safe_metrics",
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected to the database")
    except pymysql.MySQLError as e:
        print("Error connecting to MySQL database")
        print(e)
        return

    with conn.cursor() as cur:
        print("Executing SQL query")
        cur.execute("SELECT * FROM VwArtPipelineEfficiencyConfigurations")

        for row in cur:
            print("Looping through result")
            data.append(row)

    print("Preparing to commit")
    conn.commit()

    print("Finished")
    return {"config": data}
