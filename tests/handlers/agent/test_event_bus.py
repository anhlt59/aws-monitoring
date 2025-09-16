# import json
#
#
# def test_handle_monitoring_events():
#     from src.infra.aws.eventbridge import EventBridgeService, EventsRequestEntry
#     from tests.conftest import TEST_DIR
#     from tests.mock import load_events, truncate_event_table
#
#     truncate_event_table()
#
#     service = EventBridgeService()
#     for event in load_events(file_path=TEST_DIR / "data" / "guardduty_event.json"):
#         service.publish_events(
#             [
#                 EventsRequestEntry(
#                     Source="monitoring.agent.health",
#                     DetailType=event.detail_type,
#                     Detail=json.dumps(event.detail),
#                     Resources=event.resources,
#                 )
#             ]
#         )
