#!/usr/bin/python3
import os
import time
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
from itertools import islice

import boto3
from boto3.dynamodb.conditions import Key
from dateutil.parser import parse

CURRENT_DIR = os.path.dirname(__file__)
INPUT_PATH = f"{CURRENT_DIR}/data/sensors.json"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

boto3.setup_default_session(profile_name="nbdb")
dynamo_resource = boto3.resource("dynamodb", region_name="ap-southeast-1")
table = dynamo_resource.Table("denaribots-dev")


def get_dynamo_items(**query_params):
    response = table.query(**query_params)
    for item in response.get("Items", []):
        yield item

    start_key = response.get("LastEvaluatedKey")
    if start_key:
        print(f"ExclusiveStartKey={start_key}")
        query_params.update(ExclusiveStartKey=start_key)
        next_items = get_dynamo_items(**query_params)
        for item in next_items:
            yield item


def chunks(objs, limit: int):
    objs = iter(deepcopy(objs))
    while True:
        batch = list(islice(objs, limit))
        if not batch:
            break
        yield batch


def main():
    imei = "350457796260691"
    since = "2023-04-22 00:00:00"
    until = "2023-04-22 23:59:59"
    items = list(
        get_dynamo_items(KeyConditionExpression=Key("IMEI").eq(imei) & Key("sensor_time").between(since, until))
    )

    with table.batch_writer() as batch:
        for day in range(90, 101):
            for chunk in chunks(items, 25):
                for item in chunk:
                    sensor_time = parse(item["sensor_time"]) + timedelta(days=day)
                    server_time = parse(item["server_time"]) + timedelta(days=day)

                    item["IMEI"] = "350457796000010"
                    item["sensor_time"] = sensor_time.strftime(DATETIME_FORMAT)
                    item["server_time"] = server_time.strftime(DATETIME_FORMAT)
                    item["timestamp"] = Decimal(server_time.timestamp())
                    item["topic"] = item["topic"].replace("350457796260691", item["IMEI"])

                    print(item["IMEI"], item["sensor_time"])
                    batch.put_item(Item=item)

                time.sleep(0.5)
            time.sleep(0.5)
            print("day", day)


if __name__ == "__main__":
    main()
