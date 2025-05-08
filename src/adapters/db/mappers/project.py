from src.adapters.db.models.project import ProjectPersistence
from src.models.project import Project

from .base import BaseMapper


class ProjectMapper(BaseMapper):
    @classmethod
    def to_persistence(cls, model: Project) -> ProjectPersistence:
        return ProjectPersistence(
            pk=model.id,
            gsi1sk=f"NAME#{model.name.lower().replace(' ', '')}",
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_entity(cls, persistence: ProjectPersistence) -> Project:
        return Project(
            id=persistence.pk,
            name=persistence.name,
            description=persistence.description,
            created_at=persistence.created_at,
            updated_at=persistence.updated_at,
        )
