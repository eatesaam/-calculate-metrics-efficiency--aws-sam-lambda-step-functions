import json
import boto3
import os
import pandas as pd
import base64
from botocore.exceptions import ClientError
from requests.auth import HTTPBasicAuth
import requests
from datetime import datetime
import datetime as dt

def get_secret():

    secret_name = os.getenv("JIRA_CREDENTIALS_SECRET_NAME")
    region_name = "eu-west-2"

    print("Secret name:")
    print(secret_name)

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the "GetSecretValue" API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except:
        print("Got an error whilst getting the secret")
    else:
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]

            secret_content = json.loads(secret)

            return secret_content
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response["SecretBinary"])

            return json.loads(str(decoded_binary_secret))



def lambda_handler(event, context):

    print("Getting secret")
    secret = get_secret()

    print("Got the secret")
    
    # jira credentials
    jira_url = secret.get("jira_url")
    email = secret.get("email")
    api_token = secret.get("api_token")

    # call gat_issues() function
    data = get_issues(event, jira_url,email,api_token)
    # caculate days from release-analysis
    data["days"] = (data["release"] - data["analysis"]).dt.days
    # find min issue key
    mindf = pd.DataFrame()
    mindf= data.loc[data.groupby(["configID"]).days.idxmin()]
    mindf_list = mindf.values.tolist()
    # find max issue key
    maxdf = pd.DataFrame()
    maxdf= data.loc[data.groupby(["configID"]).days.idxmax()]
    maxdf_list = maxdf.values.tolist()
    
    da = pd.DataFrame()
    # calculate minimum days
    da['minimum'] = data.groupby(["configID"])['days'].min()
    # calculate maximum days
    da['maximum'] = data.groupby(["configID"])['days'].max()
    # calculate average days
    da['average'] = data.groupby(["configID"])['days'].mean()
    # convert all issues column into list
    da['issues'] = data.groupby("configID")['issue'].apply(list)
    # convert config Id column into list
    da['artId'] = data.groupby("configID")['artID'].apply(list)
    # convert dataframe to list
    data_list = da.values.tolist()
    
    # get index of dataframe
    inde = da.index
    # convert indes of dataframe to list
    ind = list(inde)
    # initialize the list that pass in return
    items = list()
    # creating the output 
    for val, inds, mnls, mxls in zip(data_list, ind, mindf_list, maxdf_list):
        configid = inds
        minimum = val[0]
        maximum = val[1]
        average = val[2]
        issues = val[3]
        con= val[4]
        art= con[0]
        minissue = mnls[2]
        maxissue = mxls[2]

        item = {
            "art": art,
            "minimum": int(minimum),
            "maximum": int(maximum),
            "average": int(average),
            "config": configid,
            "minissue": minissue,
            "maxissue": maxissue,
            "issues": issues
            
        }   

        items.append(item)

    return {"efficiency": items}
    


# fetching issues data from jira
def fecth_data(jql, jiraUrl, email, apiToken, startField, endField, startAt, maxResults):
    print("Enter in fetch_data()")

    headers = {"Accept": "application/json"}

    url = f"{jiraUrl}/rest/api/2/search?jql={jql}&fields={startField},{endField}"

    auth = HTTPBasicAuth(email, apiToken)

    query = {
        "startAt": str(startAt),
        "maxResults": str(maxResults)
    }
    # get response data from jira apis
    response = requests.request(
        "GET",
        url=url,
        headers=headers,
        params=query,
        auth=auth
    )
    # return response data
    return response.json()


# getting issues
def get_issues(arts,jiraUrl,email,apiToken):
    print("Enter in get_issues()")
    # initialize list that is passed in dataframe rows
    row = []
    
    count = 0

    for art in arts:
        startAt = 0
        maxResults = 50
        count += 1
        print(art)
        print(count)
        
        non = []
        artId = art["ArtID"]
        configId = art["ConfigID"]
        program_level_key = art["JiraProgramLevelKey"]
        start_field_key = art["StartFieldKey"]
        start_field_name = art["StartFieldName"]
        end_field_key = art["EndFieldKey"]
        end_field_name = art["EndFieldName"]
        extra_jql = art["ExtraJQL"]
        # preparing a JQL for jira api url
        jql = f"Project = {program_level_key} AND '{start_field_name}' IS NOT EMPTY AND '{end_field_name}' IS NOT EMPTY"
        print(jql)
        if extra_jql:
            jql = jql + " " + extra_jql
            print(jql)
        # fecthing the result from jira
        data = fecth_data(jql, jiraUrl, email, apiToken, start_field_key, end_field_key,startAt, maxResults)

        total = data["total"]

        issues = data["issues"]

        for issue in issues:
            key = issue.get("key")
            non.append(key)
            analysis = issue.get("fields").get(start_field_key)
            release = issue.get("fields").get(end_field_key)
            # convert analysis string to datetime
            datetimes_analysis = analysis.split("T")
            date_analysis = datetimes_analysis[0]
            times_analysis = datetimes_analysis[1]
            split_time_analysis = times_analysis.split("+")
            time_analysis = split_time_analysis[0]
            datetime_analysis = date_analysis + " " + time_analysis
            datetime_analysis = datetime.strptime(datetime_analysis, '%Y-%m-%d %H:%M:%S.%f')
            # convert release string to datetime
            datetimes_release = release.split("T")
            date_release = datetimes_release[0]
            times_release = datetimes_release[1]
            split_time_release = times_release.split("+")
            time_release = split_time_release[0]
            datetime_release = date_release + " " + time_release
            datetime_release = datetime.strptime(datetime_release, '%Y-%m-%d %H:%M:%S.%f')
            # release - analysis
            condition = datetime_release - datetime_analysis
            # 5 days
            days = dt.timedelta(days=5)
            # only append in row by (release-analysis) > 5 days
            if condition> days:
                print("appended")
                row.append((artId, configId, key, datetime_analysis, datetime_release))
            
            

        while (len(non) < total):
            startAt += maxResults
            data = fecth_data(jql, jiraUrl, email, apiToken, start_field_key, end_field_key,startAt, maxResults)

            issues = data["issues"]

            for issue in issues:
                key = issue.get("key")
                non.append(key)
                analysis = issue.get("fields").get(start_field_key)
                release = issue.get("fields").get(end_field_key)
                #  convert analysis string to datetime
                datetimes_analysis = analysis.split("T")
                date_analysis = datetimes_analysis[0]
                times_analysis = datetimes_analysis[1]
                split_time_analysis = times_analysis.split("+")
                time_analysis = split_time_analysis[0]
                datetime_analysis = date_analysis + " " + time_analysis
                datetime_analysis = datetime.strptime(datetime_analysis, '%Y-%m-%d %H:%M:%S.%f')
                # convert release string to datetime
                datetimes_release = release.split("T")
                date_release = datetimes_release[0]
                times_release = datetimes_release[1]
                split_time_release = times_release.split("+")
                time_release = split_time_release[0]
                datetime_release = date_release + " " + time_release
                datetime_release = datetime.strptime(datetime_release, '%Y-%m-%d %H:%M:%S.%f')
                # release - analysis
                condition = datetime_release - datetime_analysis
                # 5 days
                days = dt.timedelta(days=5)
                # only append in row by (release-analysis) > 5 days
                if condition > days:
                    print("appended")
                    row.append((artId, configId, key, datetime_analysis, datetime_release))
                
                
        # add all issues and their related data in dataframe
        result = pd.DataFrame(
            row, columns=["artID", "configID", "issue", "analysis", "release"])
    # return issues dataframe
    return result
