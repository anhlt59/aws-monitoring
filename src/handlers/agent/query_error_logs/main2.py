# import calendar
# import json
# import os
# import time
# import urllib.parse
# import urllib.request

# import boto3


# def getCurrentTime():
#     currentTimeGMT = time.gmtime()
#     formatMinuteCurrentTimeGMT = currentTimeGMT.tm_min
#     stringFormatTime = "%Y-%m-%d %H:" + str(formatMinuteCurrentTimeGMT) + ":00"
#     zeroSecond = time.strftime(stringFormatTime, currentTimeGMT)
#     unixTime = calendar.timegm(time.gmtime(time.mktime(time.strptime(zeroSecond, "%Y-%m-%d %H:%M:%S"))))

#     return unixTime


# def queryCloudWatchInsight(LogGroupName, Query, TimeExecute):
#     client = boto3.client("logs")
#     query = Query
#     logGroup = LogGroupName

#     endTime = int(getCurrentTime() - 1)
#     startTime = int(getCurrentTime() - int(TimeExecute))

#     print("[INFO] Start time........" + str(time.ctime(startTime)))
#     print("[INFO] End time........" + str(time.ctime(endTime)))

#     start_query_response = client.start_query(
#         logGroupName=logGroup,
#         startTime=startTime,
#         endTime=endTime,
#         queryString=query,
#     )

#     query_id = start_query_response["queryId"]

#     response = None
#     while response == None or response["status"] == "Running":
#         print("Waiting for query to complete ...")
#         time.sleep(1)
#         response = client.get_query_results(queryId=query_id)

#     valueCustomMetric = response["results"]
#     return response["results"]


# def resolveData(Data):
#     results = []
#     for item in Data:
#         results.append(item[1]["value"])
#     return results


# def resolveTitleAttachment(LogGroupName, Region):
#     return "CloudWatch | LogGroupName: " + LogGroupName + " | Region: " + Region


# def notifySlack(WebHookUrl, Message):
#     json_data = json.dumps(Message)
#     data = json_data.encode("ascii")
#     headers = {"Content-Type": "application/json"}
#     req = urllib.request.Request(WebHookUrl, data, headers)
#     resp = urllib.request.urlopen(req)
#     response = resp.read()
#     print(response)


# def pushNotifySlack(WebHookUrl, Data, Title):
#     print(Data)
#     for item in Data:
#         message = {"attachments": [{"text": "```" + item + "```", "color": "#Be3125", "title": Title}]}
#         notifySlack(WebHookUrl, message)


# def init():
#     queryStringApp = os.environ["QUERY_STRING_APP"]
#     queryStringSys = os.environ["QUERY_STRING_SYS"]
#     logGroupName = os.environ["LOG_GROUP_NAME"]
#     timeExecute = os.environ["TIME_EXECUTE"]
#     webhookUrl = os.environ["WEBHOOK"]
#     region = os.environ["REGION"]

#     dataApp = queryCloudWatchInsight(logGroupName, queryStringApp, timeExecute)
#     # dataSys = queryCloudWatchInsight(logGroupName,queryStringSys,timeExecute)

#     dataForMessageSlackApp = resolveData(dataApp)
#     # dataForMessageSlackSys = resolveData(dataSys)

#     dataSlackTitle = resolveTitleAttachment(logGroupName, region)

#     pushNotifySlack(webhookUrl, dataForMessageSlackApp, dataSlackTitle)
#     # pushNotifySlack(webhookUrl, dataForMessageSlackSys, dataSlackTitle)


# def lambda_handler(event, context):
#     init()
#     return {"statusCode": 200, "body": json.dumps("Lambda Success")}
