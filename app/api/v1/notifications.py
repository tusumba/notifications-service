import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy import delete, update
from sqlalchemy.dialects.postgresql import insert
from tusumba_common import ApiError, CurrentUser, get_current_user

from app.db import Session
from app.models import DeviceToken, NotificationSettings

router = APIRouter(prefix="/me", tags=["notifications"])
User = Annotated[CurrentUser, Depends(get_current_user)]


class SettingsBody(BaseModel):
    push_enabled: bool
    email_enabled: bool


class DeviceRegistration(BaseModel):
    platform: Literal["android"]
    token: str = Field(min_length=1)


class DeviceCreated(BaseModel):
    id: uuid.UUID
    platform: Literal["android"]
    token: str


@router.get("/notification-settings")
async def get_settings(user: User, db: Session) -> SettingsBody:
    row = await db.get(NotificationSettings, uuid.UUID(user.id))
    if row is None:
        return SettingsBody(push_enabled=True, email_enabled=True)
    return SettingsBody(push_enabled=row.push_enabled, email_enabled=row.email_enabled)


@router.put("/notification-settings")
async def put_settings(user: User, db: Session, body: SettingsBody) -> SettingsBody:
    statement = insert(NotificationSettings).values(
        user_id=uuid.UUID(user.id),
        push_enabled=body.push_enabled,
        email_enabled=body.email_enabled,
    )
    await db.execute(
        statement.on_conflict_do_update(
            index_elements=[NotificationSettings.user_id],
            set_={
                "push_enabled": body.push_enabled,
                "email_enabled": body.email_enabled,
            },
        )
    )
    await db.commit()
    return body


@router.post("/devices", status_code=201)
async def register_device(
    user: User, db: Session, body: DeviceRegistration, response: Response
) -> DeviceCreated:
    device_id = uuid.uuid4()
    inserted = await db.scalar(
        insert(DeviceToken)
        .values(id=device_id, user_id=uuid.UUID(user.id), platform=body.platform, token=body.token)
        .on_conflict_do_nothing(index_elements=[DeviceToken.token])
        .returning(DeviceToken.id)
    )
    if inserted is None:
        response.status_code = 200
        existing = await db.scalar(
            update(DeviceToken)
            .where(DeviceToken.token == body.token)
            .values(user_id=uuid.UUID(user.id), platform=body.platform)
            .returning(DeviceToken.id)
        )
        if existing is None:
            raise RuntimeError("Device token disappeared during registration")
        device_id = existing
    await db.commit()
    return DeviceCreated(id=device_id, platform=body.platform, token=body.token)


@router.delete("/devices/{id}", status_code=204)
async def delete_device(user: User, db: Session, id: uuid.UUID) -> Response:
    removed = await db.scalar(
        delete(DeviceToken)
        .where(DeviceToken.id == id, DeviceToken.user_id == uuid.UUID(user.id))
        .returning(DeviceToken.id)
    )
    if removed is None:
        raise ApiError(404, "device_not_found", "Устройство не найдено.")
    await db.commit()
    return Response(status_code=204)
