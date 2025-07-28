# import json
#
#
# def handle_monitoring_events():
#     import boto3
#
#     boto3.setup_default_session(profile_name="lc-stg")
#
#     from src.adapters.aws.eventbridge import EventBridgeService, EventsRequestEntry
#     from tests.conftest import TEST_DIR
#     from tests.mock import load_events
#
#     service = EventBridgeService()
#     for event in load_events(file_path=TEST_DIR / "data" / "alarm_event.json"):
#         service.publish_events(
#             [
#                 EventsRequestEntry(
#                     Source=event.source.replace("aws.", "monitoring.agent."),
#                     DetailType=event.detail_type,
#                     Detail=json.dumps(event.detail),
#                     Resources=event.resources,
#                 )
#             ]
#         )
#
#
# # if __name__ == "__main__":
# #     handle_monitoring_events()
