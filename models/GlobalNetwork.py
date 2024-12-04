import asyncio
from mytoolit.can.network import Network


class NetworkSingleton:
    """
    This class serves as a wrapper around the MyToolIt Network class.
    This is required as a REST API is inherently stateless and thus to stay within one Network,
    we need to pass it by reference to all functions. Otherwise, after every call to an endpoint,
    the network is closed and the devices reset to their default parameters. This is intended behavior,
    but unintuitive for a dashboard where the user should feel like continuously working with devices.

    Dependency injection: See https://fastapi.tiangolo.com/tutorial/dependencies/
    """
    _instance: Network | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def create_instance_if_none(cls):
        async with cls._lock:
            if cls._instance is None:
                cls._instance = Network()
                await cls._instance.__aenter__()
                print(f"Created Network instance with ID <{id(cls._instance)}>")

    @classmethod
    async def get_instance(cls):
        await cls.create_instance_if_none()
        print(f"Using Network instance with ID <{id(cls._instance)}>")
        return cls._instance

    @classmethod
    async def close_instance(cls):
        async with cls._lock:
            if cls._instance is not None:
                print(f"Shutting down Network instance with ID <{id(cls._instance)}>")
                await cls._instance.__aexit__(None, None, None)
                print(f"Shut down Network instance with ID <{id(cls._instance)}>")
                cls._instance = None

    @classmethod
    def has_instance(cls):
        return cls._instance is not None


async def get_network() -> Network:
    network = await NetworkSingleton.get_instance()
    return network
