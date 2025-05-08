from typing import Annotated

from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.openapi.params import Query

from src.adapters.api.settings import cors_config
from src.models.account import AccountCreateDTO, AccountUpdateDTO
from src.usecases.account import create_account, delete_account, get_account, list_accounts, update_account

app = APIGatewayRestResolver(cors=cors_config, enable_validation=True)


@app.post("/projects/<project_id>/accounts")
def create(project_id: str, dto: AccountCreateDTO):
    # id is generated or provided by client, ensure it's handled in usecase
    dto.project_id = project_id
    account = create_account(dto)
    return {"id": account.id}


@app.get("/projects/<project_id>/accounts/<account_id>")
def get(project_id: str, account_id: str):
    return get_account(project_id, account_id)


@app.get("/projects/<project_id>/accounts")
def _list(
    project_id: str,
    limit: Annotated[int, Query] = 50,
    direction: Annotated[str, Query] = "asc",
    cursor: Annotated[str, Query] = None,
):
    return list_accounts(project_id, limit, direction, cursor)


@app.put("/projects/<project_id>/accounts/<account_id>")
def update(project_id: str, account_id: str, dto: AccountUpdateDTO):
    update_account(project_id, account_id, dto)
    return {"id": account_id}


@app.delete("/projects/<project_id>/accounts/<account_id>")
def delete(project_id: str, account_id: str):
    delete_account(project_id, account_id)
