# Модель данных Notifications

Задача: [#18893 - OpenAPI v1 и модель данных: Notifications](https://ai.nsu.ru/issues/18893).
Источник: [архитектура Tusumba](https://ai.nsu.ru/projects/tusumba/wiki/Архитектура),
раздел «Notifications (notifications_db)» и [ER-диаграмма](https://ai.nsu.ru/attachments/download/6818/er-notifications-db.png).

## notification_settings

Настройки получения push и email.

| Поле | Тип | Ключ |
|---|---|---|
| user_id | uuid | PK |
| push_enabled | boolean | |
| email_enabled | boolean | |

## device_tokens

Токены FCM устройств Android.

| Поле | Тип | Ключ |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | |
| platform | enum (android) | |
| token | text | |

## notifications

История и очередь уведомлений.

| Поле | Тип | Ключ |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | |
| type | text | |
| payload | jsonb | |
| status | enum (queued, sent, failed) | |
| created_at | timestamptz | |

## Внешние связи

`device_tokens.user_id`, `notification_settings.user_id` и `notifications.user_id`
ссылаются на `identity_db.users.id` по идентификатору, без внешнего ключа.

## API

| Запрос | Назначение | Доступ |
|---|---|---|
| GET /v1/me/notification-settings | Настройки push и email | Пользователь |
| PUT /v1/me/notification-settings | Сохранение настроек push и email | Пользователь |
| POST /v1/me/devices | Регистрация токена устройства | Пользователь |
| DELETE /v1/me/devices/{id} | Удаление токена устройства | Пользователь |

## Поведение по требованию #18119

Источник: [Получение и настройка уведомлений](https://ai.nsu.ru/issues/18119).

- Пользователь авторизован.
- При отключённых уведомлениях система не отправляет push.
- Если уведомления не разрешены на устройстве, система предлагает включить разрешение.
- При изменении настроек система сохраняет новые настройки.
- По уже прошедшему мероприятию система не отправляет напоминание.
- Открытие уведомления переводит пользователя к мероприятию, билету или записи.

Сообщения из требования:

- «Уведомления отключены.»
- «Разрешите уведомления на устройстве.»
- «Не удалось обновить настройки уведомлений. Попробуйте позже.»
