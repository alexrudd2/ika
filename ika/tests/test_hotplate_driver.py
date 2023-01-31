"""Test the hotplate driver responds with correct data."""
from random import uniform
from unittest import mock

import pytest

from ika import command_line
from ika.mock import Hotplate


@pytest.fixture
def driver():
    """Confirm the hotplate correctly initializes."""
    return Hotplate('fakeip')


@pytest.fixture
def expected_info_response():
    """Return mocked hotplate data."""
    return {
        "name": "SPINNY HOT THING",
        "temp_limit": 150.0,
        "device_type": 1,
    }


@mock.patch('ika.Hotplate', Hotplate)
def test_driver_cli_with_info(capsys):
    """Confirm the commandline interface works."""
    command_line(['fakeip', '--type', 'hotplate'])
    captured = capsys.readouterr()
    assert "temp_limit" in captured.out
    assert "name" in captured.out


@mock.patch('ika.Hotplate', Hotplate)
def test_driver_cli(capsys):
    """Confirm the commandline interface works with --no-info."""
    command_line(['fakeip', '--type', 'hotplate', '--no-info'])
    captured = capsys.readouterr()
    assert "temp" in captured.out
    assert "name" not in captured.out


async def test_get_response(driver, expected_info_response):
    """Confirm that the driver returns correct values on get_info() calls."""
    assert expected_info_response == await driver.get_info()


async def test_readme_example(expected_info_response):
    """Confirm the readme example using an async context manager works."""
    async def get():
        async with Hotplate('hotplate-ip.local') as device:
            response = await device.get()       # Get speed, torque, temp, setpoints
            assert "process_temp" in response
            assert expected_info_response == await device.get_info()  # Get name
    await get()


async def test_setpoint_roundtrip():
    """Confirm that setpoints can be updated."""
    async def get():
        async with Hotplate('hotplate-ip.local') as device:
            process_sp = round(uniform(15, 100), 2)
            surface_sp = round(uniform(30, 150), 2)
            await device.set(equipment='process', setpoint=process_sp)
            await device.set(equipment='surface', setpoint=surface_sp)
            response = await device.get()
            assert process_sp == response['process_temp']['setpoint']
            assert surface_sp == response['surface_temp']['setpoint']
    await get()
