import uuid

import httpx2
import pytest
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tusumba_common import CurrentUser, get_current_user

from app.models import DeviceToken


@pytest.fixture
def user_client(
    app: FastAPI, client: httpx2.AsyncClient
) -> tuple[httpx2.AsyncClient, dict[str, uuid.UUID]]:
    current = {"id": uuid.uuid4()}

    async def user() -> CurrentUser:
        return CurrentUser(id=str(current["id"]))

    app.dependency_overrides[get_current_user] = user
    return client, current


async def test_settings_require_authentication(client: httpx2.AsyncClient) -> None:
    response = await client.get("/v1/me/notification-settings")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "not_authenticated"


async def test_invalid_device_uses_common_error_format(
    user_client: tuple[httpx2.AsyncClient, dict[str, uuid.UUID]],
) -> None:
    client, _ = user_client
    response = await client.post("/v1/me/devices", json={"platform": "android", "token": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


async def test_settings_are_saved_per_user(
    user_client: tuple[httpx2.AsyncClient, dict[str, uuid.UUID]],
) -> None:
    client, current = user_client
    path = "/v1/me/notification-settings"
    assert (await client.get(path)).json() == {"push_enabled": True, "email_enabled": True}

    response = await client.put(path, json={"push_enabled": True, "email_enabled": False})
    assert response.status_code == 200
    assert (await client.get(path)).json() == {"push_enabled": True, "email_enabled": False}

    current["id"] = uuid.uuid4()
    assert (await client.get(path)).json() == {"push_enabled": True, "email_enabled": True}


async def test_device_can_only_be_deleted_by_owner(
    user_client: tuple[httpx2.AsyncClient, dict[str, uuid.UUID]], session: AsyncSession
) -> None:
    client, current = user_client
    owner = current["id"]
    fcm_value = "fcm-token"
    response = await client.post("/v1/me/devices", json={"platform": "android", "token": fcm_value})
    assert response.status_code == 201
    device_id = uuid.UUID(response.json()["id"])
    assert response.json()["platform"] == "android"
    assert response.json()["token"] == fcm_value

    repeated = await client.post("/v1/me/devices", json={"platform": "android", "token": fcm_value})
    assert repeated.status_code == 200
    assert uuid.UUID(repeated.json()["id"]) == device_id

    current["id"] = uuid.uuid4()
    forbidden = await client.delete(f"/v1/me/devices/{device_id}")
    assert forbidden.status_code == 404
    assert forbidden.json()["error"]["code"] == "device_not_found"
    row = await session.scalar(select(DeviceToken).where(DeviceToken.id == device_id))
    assert row is not None and row.user_id == owner

    current["id"] = owner
    assert (await client.delete(f"/v1/me/devices/{device_id}")).status_code == 204
    session.expire_all()
    assert await session.get(DeviceToken, device_id) is None
    assert (await client.delete(f"/v1/me/devices/{device_id}")).status_code == 404


async def test_repeated_token_moves_to_current_user(
    user_client: tuple[httpx2.AsyncClient, dict[str, uuid.UUID]], session: AsyncSession
) -> None:
    client, current = user_client
    first_user = current["id"]
    body = {"platform": "android", "token": "transfer-fcm-value"}
    created = await client.post("/v1/me/devices", json=body)
    assert created.status_code == 201

    current["id"] = uuid.uuid4()
    repeated = await client.post("/v1/me/devices", json=body)
    assert repeated.status_code == 200
    assert repeated.json()["id"] == created.json()["id"]

    session.expire_all()
    row = await session.get(DeviceToken, uuid.UUID(created.json()["id"]))
    assert row is not None and row.user_id == current["id"]

    current["id"] = first_user
    assert (await client.delete(f"/v1/me/devices/{row.id}")).status_code == 404
