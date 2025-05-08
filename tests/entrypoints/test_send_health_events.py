from src.entrypoints.send_health_events.main import handler

event = {
    "version": "0",
    "id": "12345678-1234-1234-1234-123456789012",
    "detail-type": "AWS Health Event",
    "source": "aws.health",
    "account": "123456789012",
    "time": "2023-08-29T03:13:27Z",
    "region": "us-east-1",
    "resources": [],
    "detail": {
        "eventArn": "arn:aws:health:us-east-1::event/EC2/PLANNED_LIFECYCLE_EVENT/AWS_EC2_MAINTENANCE_SCHEDULED_1693278720289",
        "service": "EC2",
        "eventScopeCode": "ACCOUNT_SPECIFIC",
        "communicationId": "32157c62a5a64a33ec5445c5c77f941128b345fa1fe98bbd8ffd7a4a708323bf",
        "lastUpdatedTime": "Tue, 29 Aug 2023 03:13:27 GMT",
        "statusCode": "upcoming",
        "eventRegion": "us-east-1",
        "eventTypeCode": "AWS_EC2_MAINTENANCE_SCHEDULED",
        "eventTypeCategory": "scheduledChange",
        "startTime": "Tue, 29 Aug 2023 03:30:00 GMT",
        "eventDescription": [
            {"language": "en_US", "latestDescription": "This is a test AWS Health Event AWS_EC2_MAINTENANCE_SCHEDULED"}
        ],
        "affectedEntities": [
            {
                "entityValue": "arn:ec2-1-101002929",
                "lastupdatedTime": "Thu, 26 Jan 2023 19:01:55 GMT",
                "status": "PENDING",
                "tags": {},
            },
            {
                "entityValue": "arn:ec2-1-101002930",
                "lastupdatedTime": "Thu, 26 Jan 2023 19:05:12 GMT",
                "status": "RESOLVED",
                "tags": {},
            },
            {
                "entityValue": "arn:ec2-1-101002931",
                "lastupdatedTime": "Thu, 26 Jan 2023 19:07:13 GMT",
                "status": "UPCOMING",
                "tags": {},
            },
            {
                "entityValue": "arn:ec2-1-101002932",
                "lastupdatedTime": "Thu, 26 Jan 2023 19:10:59 GMT",
                "status": "RESOLVED",
                "tags": {},
            },
        ],
        "affectedAccount": "123456789012",
    },
}


def test_send_health_events():
    response = handler(event, None)
    assert response is None
