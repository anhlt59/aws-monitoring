from src.adapters.db.mappers import ProjectMapper
from src.adapters.db.models import ProjectPersistence
from src.adapters.db.repositories.base import DynamoRepository, QueryResult
from src.common.exceptions.http import ConflictError, NotFoundError, UnprocessedError
from src.models import Project

ProjectQueryResult = QueryResult[Project]


class ProjectRepository(DynamoRepository):
    model_cls = ProjectPersistence

    def get_by_id(self, id: str) -> Project:
        model = self._get(hash_key=id, range_key="METADATA")
        return ProjectMapper.to_entity(model)

    def get_by_name(self, name: str) -> Project:
        result = self._query(
            hash_key="PROJECT",
            range_key_condition=ProjectPersistence.gsi1sk == name.lower().replace(" ", ""),
            index=ProjectPersistence.gsi1,
        )
        if project := next(result, None):
            return ProjectMapper.to_entity(project)
        raise NotFoundError(f"Project<name={name}> not found")

    def list(self, limit: int = 50, direction: str = "asc", cursor: dict | None = None) -> ProjectQueryResult:
        result = self._query(
            hash_key="PROJECT",
            index=ProjectPersistence.gsi1,
            last_evaluated_key=cursor,
            scan_index_forward="asc" == direction,
            limit=limit,
        )
        return ProjectQueryResult(
            items=[ProjectMapper.to_entity(project) for project in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: Project):
        count = self._count(
            hash_key="PROJECT",
            range_key_condition=ProjectPersistence.gsi1sk == entity.name.lower().replace(" ", ""),
            index=ProjectPersistence.gsi1,
        )
        if count > 0:
            raise ConflictError(f"Project<name='{entity.name}'> already exists")
        model = ProjectMapper.to_persistence(entity)
        self._create(model)

    def update(self, id: str, attributes: dict):
        if name := attributes.get("name"):
            attributes["gsi1sk"] = name.lower()
        try:
            self._update(hash_key=id, range_key="METADATA", attributes=attributes)
        except UnprocessedError:
            raise NotFoundError(f"Project<id={id}> not found")

    def delete(self, id: str):
        try:
            self._delete(hash_key=id, range_key="METADATA")
        except UnprocessedError:
            raise NotFoundError(f"Project<id={id}> not found")
