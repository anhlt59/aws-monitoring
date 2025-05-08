from src.adapters.db.repositories import AccountRepository, ProjectRepository
from src.common.utils.encoding import base64_to_json, json_to_base64
from src.models.project import Project, ProjectCreateDTO, ProjectUpdateDTO

project_repo = ProjectRepository()
account_repo = AccountRepository()


def get_project(project_id: str):
    return project_repo.get_by_id(project_id)


def list_projects(limit=50, direction="asc", cursor: str | None = None):
    decode_cursor = base64_to_json(cursor) if cursor else None
    result = project_repo.list(limit, direction, decode_cursor)
    return {
        "items": result.items,
        "limit": limit,
        "next": json_to_base64(result.cursor) if result.cursor else None,
        "previous": cursor,
    }


def create_project(dto: ProjectCreateDTO):
    project = Project.model_validate(dto, from_attributes=True)
    project_repo.create(project)
    return project


def update_project(project_id: str, dto: ProjectUpdateDTO):
    project_repo.update(project_id, dto.model_dump())


def delete_project(project_id: str):
    project_repo.delete(project_id)
    # Clean up associated accounts
    accounts = account_repo.list_by_project(project_id).items
    for account in accounts:
        account_repo.delete(project_id, account.id)
