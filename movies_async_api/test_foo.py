import pytest
import aiohttp
import asyncio

@pytest.fixture(scope='session')
async def session():
    print("setup")
    session = aiohttp.ClientSession()
    yield session
    print("teardown")
    #await session.close()

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def _flush_event_loop(event_loop):
    yield
    event_loop.flush()

@pytest.mark.asyncio
async def test_1(session):
    await session.get('http://0.0.0.0:8000/v1/film/')


@pytest.mark.asyncio
async def test_2(session):
    await session.get('http://0.0.0.0:8000/v1/film/')