import os

os.environ.setdefault("STAGE", "local")
os.environ.setdefault("AWS_REGION", "us-east-1")

if __name__ == "__main__":
    from domain.use_cases.users.create_user import CreateUser, CreateUserDTO, UserRole

    create_user_uc = CreateUser()
    dto = CreateUserDTO(
        email="admin@yopmail.com",
        password="12345678",
        full_name="Admin User",
        role=UserRole.ADMIN,
    )
    create_user_uc.execute(dto)
