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

    art_abbreviation = event['pathParameters']['art_abbreviation']

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
        cur.execute(f"SELECT * FROM VwArtPipelineEfficiencies WHERE ArtAbbreviation = '{art_abbreviation}'")
        result = cur.fetchall()

        for row in result:
            print("Looping through result")
            ArtID = row['ArtID']
            ArtName = row['ArtName']
            ArtAbbreviation = row['ArtAbbreviation']
            EfficiencyID = row['EfficiencyID']
            Minimum = row['Minimum']
            Average = row['Average']
            Maximum = row['Maximum']
            PipelineEfficiencyDate = row['PipelineEfficiencyDate']
            IssueKeys = row['IssueKeys']
            MinIssueKey = row['MinIssueKey']
            MaxIssueKey = row['MaxIssueKey']
            ConfigurationName = row['ConfigurationName']
            ConfigurationCode = row['ConfigurationCode']
            
            item = {
                "ArtID": ArtID,
                "ArtName": ArtName,
                "ArtAbbreviation": ArtAbbreviation,
                "EfficiencyID": EfficiencyID,
                "Minimum": Minimum,
                "Average": Average,
                "Maximum": Maximum,
                "PipelineEfficiencyDate": str(PipelineEfficiencyDate),
                "IssueKeys": IssueKeys,
                "MinIssueKey": MinIssueKey,
                "MaxIssueKey": MaxIssueKey,
                "ConfigurationName": ConfigurationName,
                "ConfigurationCode": ConfigurationCode
            }
            
            data.append(item)

    print("Preparing to commit")
    conn.commit()

    print("Finished")
    # return {
    #     "statusCode": 200,
    #     "body": json.dumps(data)
    # }
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(data)
    }
