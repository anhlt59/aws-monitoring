import time
from datetime import datetime
from time import sleep
from typing import Iterable, Type, TypeVar

from pynamodb.exceptions import AttributeDeserializationError
from pynamodb.models import Model

from src.constants import DYNAMODB_DEFAULT_BATCH_DELAY, DYNAMODB_DEFAULT_BATCH_SIZE
from src.logger import logger
from src.models.sensors import SensorModel
from src.utils import chunks

DynamoT = TypeVar("DynamoT", bound=Model)


class PutItemError(Exception):
    failed_items: list[SensorModel]

    def __init__(self, *args, failed_items=None):
        self.failed_items = failed_items or []
        super().__init__(*args)


class DynamoRepository:
    model_class: Type[DynamoT]
    logger = logger

    def deserialize(self, document: dict) -> DynamoT:
        try:
            return self.model_class().from_raw_data(document)
        except AttributeDeserializationError as e:
            self.logger.error(f"Deserialize error: {e}")

    def get(self, hash_key: str, range_key=None) -> DynamoT:
        return self.model_class.get(hash_key, range_key=range_key)

    def create(self, item: dict | None = None, model: DynamoT | None = None):
        if item:
            model = self.model_class(**item)
        model.save()
        return model

    def bulk_create(
        self,
        items: Iterable[dict] | None = None,
        models: list[DynamoT] | None = None,
        retries=8,
        retry_delay=1,
    ) -> list[DynamoT]:
        if items:
            models = [self.model_class(**item) for item in items]

        with self.model_class.batch_write() as batch:
            try:
                for chunked_models in chunks(models, DYNAMODB_DEFAULT_BATCH_SIZE):
                    for model in chunked_models:
                        batch.save(model)
                    logger.info(f"Putted {(len(chunked_models))} items to DynamoDB: {chunked_models}")
                    time.sleep(DYNAMODB_DEFAULT_BATCH_DELAY)
            except Exception as e:
                logger.error(f"DynamoDB batchWriteItem failed: {e}")

        # retry if any error occured
        if batch.failed_operations:
            failed_items = [item["item"] for item in batch.failed_operations]
            if retries:
                logger.debug(f"Exceeded ProvisionedThroughput. Trying to retry batchWriteItem: {failed_items}")
                sleep(retry_delay)
                return self.bulk_create(models=failed_items, retries=retries - 1)
            else:
                raise PutItemError("Exceed max-retries", failed_items=failed_items)

        return models


class SensorRepository(DynamoRepository):
    model_class = SensorModel

    def list_by_imei(
        self, imei, time_range: tuple[datetime, datetime] | None = None, **kwargs
    ) -> Iterable[SensorModel]:
        range_key_condition = SensorModel.sensor_time.between(*time_range) if time_range else None
        return self.model_class.query(hash_key=imei, range_key_condition=range_key_condition, **kwargs)

    def deserialize_dynamo_records(self, records: list[dict]) -> Iterable[SensorModel]:
        for record in records:
            event_type = record.get("eventName")
            new_image = record.get("dynamodb", {}).get("NewImage")

            if event_type == "INSERT" and new_image:
                if sensor := self.deserialize(new_image):
                    # self.logger.debug(f"Deserialized record: {sensor.to_json()}")
                    yield sensor
                else:
                    self.logger.warning(f"Can't deserialize record: {record}")
            else:
                self.logger.warning(f"Invalid record: {record}")
