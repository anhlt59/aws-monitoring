from dependency_injector import containers, providers


# Services
class EmailService:
    def send_email(self, message):
        print(f"Sending email: {message}")


class UserNotifier:
    def __init__(self, email_service):
        self.email_service = email_service

    def notify(self, message):
        self.email_service.send_email(message)


# Container
class Container(containers.DeclarativeContainer):
    email_service = providers.Singleton(EmailService)
    user_notifier = providers.Factory(UserNotifier, email_service=email_service)


# Usage
container = Container()
notifier = container.user_notifier()
notifier.notify("Hello!")
print(id(notifier))
