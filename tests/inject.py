from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject


class ServiceA:
    def do_something(self):
        print("ServiceA did something")


class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a

    def perform_action(self):
        print("ServiceB performed action")
        self.service_a.do_something()


class Container(containers.DeclarativeContainer):
    service_a = providers.Singleton(ServiceA)
    service_b = providers.Factory(ServiceB, service_a=service_a)


@inject
def main(service_a: ServiceA = Provide[Container.service_a], service_b: ServiceB = Provide[Container.service_b]):
    service_a.do_something()
    service_b.perform_action()


container = Container()
container.wire(modules=[__name__])
