from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    from src.adapters.db.repositories import UserRepository
    from src.domain.use_cases.auth import (
        AuthenticateUser,
        GenerateAuthTokens,
        LogoutUser,
        RefreshAuthToken,
    )

    # Repositories
    user_repository = providers.Singleton(UserRepository)
    # Use Cases
    authenticate_user_uc = providers.Factory(AuthenticateUser, user_repository=user_repository)
    generate_tokens_uc = providers.Factory(GenerateAuthTokens)
    refresh_token_uc = providers.Factory(RefreshAuthToken, user_repository=user_repository)
    logout_user_uc = providers.Factory(LogoutUser)
