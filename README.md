# notifications-service

Сервис **Notifications** системы Tusumba: push и email, настройки уведомлений, напоминания о мероприятиях.

**Ответственный:** Семён Иноков (задача #18893).

## Что делает

- подписывается на события других сервисов через RabbitMQ и создаёт уведомления;
- отправляет email (подтверждение покупки с билетом, приглашения, уведомления) через провайдера по SMTP или API;
- отправляет push на Android через FCM (Firebase Cloud Messaging);
- хранит токены устройств и настройки пользователя: включены ли push и email;
- фоновая задача рассылает напоминания о мероприятиях.

База данных `notifications_db`: `device_tokens`, `notification_settings`, `notifications`, `reminders`.

## API

Внешний: `GET` и `PUT /v1/me/notification-settings`, `POST /v1/me/devices`, `DELETE /v1/me/devices/{id}`.

Потребляет события: `FriendRequested`, `EventInvitationSent`, `EventPublished`, `EventUpdated`, `TicketPurchased`, `RegistrationChanged`, `ApplicationApproved`, `ComplaintResolved`.

Закрывает требование: #18119.

## Стек

Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic, PostgreSQL 16, RabbitMQ (FastStream), Firebase Cloud Messaging.

## Запуск

Описание появится после готовности шаблона сервиса (#18887) и стенда (#18905). Окружение целиком поднимается из репозитория `deploy`.

## Документация

- [OpenAPI v1](docs/openapi.yaml) - API раздела «Уведомления» архитектуры.
- [Модель данных](docs/data-model.md) - таблицы настроек, токенов устройств и уведомлений.

Wiki проекта: https://ai.nsu.ru/projects/tusumba/wiki/Архитектура. Контракт API: OpenAPI v1 (#18893). Задачи ведутся в Redmine: https://ai.nsu.ru/projects/tusumba. Issues и Wiki GitHub выключены.
