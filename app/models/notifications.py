import uuid

from sqlalchemy import Boolean, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    push_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)


class DeviceToken(Base):
    __tablename__ = "device_tokens"
    __table_args__ = (CheckConstraint("platform = 'android'", name="android_platform"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
