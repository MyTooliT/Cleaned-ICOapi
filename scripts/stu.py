from mytoolit.can import Network


async def get_stu_status(node: str = 'STU 1'):
    async with Network() as network:
        return await network.get_state(node)


async def get_stu_mac(node: str = 'STU 1'):
    async with Network() as network:
        return await network.get_mac_address(node)
