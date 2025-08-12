# API Gateway Documentation

| Method | Path              | Description        | Function                                                                 |
|--------|-------------------|--------------------|--------------------------------------------------------------------------|
| GET    | /events           | List events        | [Master-ListEvents](../infra/master/functions/api/Event-ListItems.yml)   |
| PUT    | /events/{eventId} | Update event by ID | [Master-UpdateEvent](../infra/master/functions/api/Event-UpdateItem.yml) |
| GET    | /agents           | List agents        | [Master-ListAgents](../infra/master/functions/api/Agent-ListItems.yml)   |
| GET    | /agents/{agentId} | Get agent by ID    | [Master-GetAgent](../infra/master/functions/api/Agent-GetItem.yml)       |
| PUT    | /agents/{agentId} | Update agent by ID | [Master-UpdateAgent](../infra/master/functions/api/Agent-UpdateItem.yml) |
