from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject


class ServiceA:
    def do_something(self):
        return "ServiceA did something"


class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a

    def perform_action(self):
        result = self.service_a.do_something()
        return f"ServiceB performed action with result: {result}"


class Container(containers.DeclarativeContainer):
    service_a = providers.Singleton(ServiceA)
    service_b = providers.Factory(ServiceB, service_a=service_a)


@inject
def main(
    service_a: ServiceA = Provide[Container.service_a],
    service_b: ServiceB = Provide[Container.service_b]
):
    service_b2 = container.service_b()
    service_a2 = container.service_a()

    print(service_b.perform_action())
    print(f"service_a is service_a2: {service_a is service_a2}")  # Should be True since Singleton
    print(f"service_b is service_b2: {service_b is service_b2}")  # Should be False since Factory


if __name__ == '__main__':
    container = Container()
    container.wire(modules=[__name__])
    main()
