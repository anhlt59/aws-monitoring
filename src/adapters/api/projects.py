from typing import Annotated

from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.openapi.params import Query

from src.adapters.api.settings import cors_config
from src.models.project import ProjectCreateDTO, ProjectUpdateDTO
from src.usecases.project import create_project, delete_project, get_project, list_projects, update_project

app = APIGatewayRestResolver(cors=cors_config, enable_validation=True)


@app.post("/projects")
def create(dto: ProjectCreateDTO):
    project = create_project(dto)
    return {"id": project.id}


@app.get("/<project_id>")
def get(project_id: str):
    return get_project(project_id)


@app.get("/projects")
def _list(
    limit: Annotated[int, Query] = 50,
    direction: Annotated[str, Query] = "asc",
    cursor: Annotated[str, Query] = None,
):
    return list_projects(limit, direction, cursor)


@app.put("/projects/<project_id>")
def update(project_id: str, dto: ProjectUpdateDTO):
    update_project(project_id, dto)
    return {"id": project_id}


@app.delete("/projects/<project_id>")
def delete(project_id: str):
    delete_project(project_id)
    return {"id": project_id}
