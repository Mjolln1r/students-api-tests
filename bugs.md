# Баг-репорты: Students API

- Стенд: `http://194.87.126.16`
- Спецификация: `http://194.87.126.16/apidocs`
- Дата тестирования: 2026-10-29
- Инструменты: Python, pytest, requests, Allure
- Воспроизведение: `pytest` (в скобках у каждого бага указан тест)

## Сводка

| ID | Кратко | Эндпоинт | Критичность |
|---|---|---|---|
| BUG-001 | Нестабильное чтение: студент то найден, то «не найден» | GET /student/{id} (затрагивает и PUT) | Critical |
| BUG-002 | Удалённый студент продолжает возвращаться | GET /student/{id} после DELETE | Critical |
| BUG-003 | Удаление несуществующего и повторное удаление возвращают success | DELETE /student/{id} | Major |
| BUG-004 | Нечисловой id: ответ HTML вместо JSON | GET /student/abc | Minor |
| BUG-005 | PUT не сохраняет gender | PUT /student/{id} | Critical |
| BUG-006 | PUT возвращает status строкой | PUT /student/{id} | Minor |
| BUG-007 | В ответе GET верхний status повторяет статус студента | GET /student/{id} | Major |

---

## BUG-001: Нестабильное чтение студента по id

**Критичность:** Critical. **Тест:** `tests/test_get_students.py::test_get_student_is_consistent`

**Шаги:**
1. `POST /student` с валидными данными (получен id, например 416).
2. Выполнить `GET /student/416` 10 раз подряд.

**Ожидаемо:** все 10 ответов одинаковые: `{"status": 1, "student": {...}}`.

**Фактически:** ответы чередуются. В прогоне студент найден в 7 из 10 запросов, в остальных:
```
HTTP 200
{"message":"Student not found","status":0}
```

**Проявления:**
- «не найден» сразу после создания (в setup тестов у студентов 413, 416, 422, 423);
- после `PUT` чтения чередуются между старыми и обновлёнными данными (студент 391, 6 запросов подряд);
- `PUT` на существующего студента иногда отвечает `{"message":"Student not found, student not updated","status":0}` (студенты 402, 422), повтор того же запроса проходит.

**Примечание:** поведение похоже на несколько экземпляров сервера с несинхронизированными данными (гипотеза, подтверждено только наблюдаемым поведением). Из-за этого в тестах положительные сценарии используют повтор запроса с таймаутом.

---

## BUG-002: Удалённый студент продолжает возвращаться

**Критичность:** Critical. **Тест:** `tests/test_delete_students.py::test_deleted_student_is_not_returned`

**Шаги:**
1. Создать студента (id 414).
2. `DELETE /student/414` → `200 {"message":"Student deleted successfully","status":1}`.
3. `GET /student/414` 10 раз подряд.

**Ожидаемо:** все 10 ответов `{"message":"Student not found","status":0}`.

**Фактически:** удалённый студент вернулся в 7 из 10 ответов:
```
HTTP 200
{"status":1,"student":{"email":"qa_fe6b51dd51@example.com","gender":"male","id":414,"name":"Ivan Ivanov","phone_no":"+79701058940","status":1}}
```

---

## BUG-003: Удаление несуществующего и повторное удаление возвращают success

**Критичность:** Major. **Тесты:** `test_delete_nonexistent_student`, `test_delete_twice` в `tests/test_delete_students.py`

**Шаги (вариант 1):** `DELETE /student/999999`.
**Шаги (вариант 2):** создать студента, дважды выполнить `DELETE /student/{id}`.

**Ожидаемо:** для несуществующего ресурса ошибка: HTTP 404 (или как минимум `{"message":"Student not found","status":0}`).

**Фактически:**
```
HTTP 200
{"message":"Student deleted successfully","status":1}
```
Это же сообщение приходит на второй `DELETE` того же id.

---

## BUG-004: Нечисловой id возвращает HTML вместо JSON

**Критичность:** Minor. **Тест:** `tests/test_get_students.py::test_non_numeric_id_returns_json`

**Шаги:** `GET /student/abc`.

**Ожидаемо:** ошибка в формате API (JSON с `status` и `message`), код 400 (или 404).

**Фактически:**
```
HTTP 404
Content-Type: text/html; charset=utf-8

<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1>...
```
Клиент, ожидающий JSON, получает исключение при разборе тела. Аналогичный HTML-ответ наблюдался и для `PUT` с нечисловым id.

---

## BUG-005: PUT не сохраняет gender

**Критичность:** Critical. **Тест:** `tests/test_put_students.py::test_update_is_persisted`

**Шаги:**
1. Создать студента (`gender: male`).
2. `PUT /student/423` с телом `{"name":"Updated Name","email":"upd_c3a3e69162@example.com","gender":"female","status":0}` → ответ содержит `"gender":"female"`.
3. Прочитать студента через `GET /student/423`, дождавшись обновлённых данных (имя `Updated Name`).

**Ожидаемо:** `gender: female`.

**Фактически:** `gender: male`, при этом `name`, `email` и `status` обновились:
```
{"status":0,"student":{"email":"upd_c3a3e69162@example.com","gender":"male","id":423,"name":"Updated Name","phone_no":"+72037340056","status":0}}
```

---

## BUG-006: PUT возвращает status строкой

**Критичность:** Minor. **Тест:** `tests/test_put_students.py::test_update_student_status_type`

**Шаги:** `PUT /student/{id}` с `"status": 0`.

**Ожидаемо (по Swagger `integer`, enum 0/1):** `"status": 0`.

**Фактически:**
```
{"message":"Student updated successfully","status":1,"student":{...,"status":"0"}}
```
Тип `string` вместо `integer` (в ответе `GET` это поле числовое).

---

## BUG-007: В ответе GET верхний status повторяет статус студента

**Критичность:** Major. **Тест:** `tests/test_get_students.py::test_get_inactive_student`

**Шаги:**
1. `POST /student` со `status: 0` (id 417).
2. `GET /student/417`.

**Ожидаемо:** студент найден, верхний `status: 1` (как у студентов со `status: 1`).

**Фактически:**
```
{"status":0,"student":{"email":"qa_59d9b657c1@example.com","gender":"male","id":417,"name":"Ivan Ivanov","phone_no":"+71885657594","status":0}}
```
Поле успешности равно статусу студента. «Найден неактивный студент» неотличим от «студент не найден» (там тоже `status: 0`).

---

## Замечания (не баги)

1. **HTTP 200 на ошибки.** Все ошибки (студент не найден, неверные данные в POST и PUT) приходят с кодом 200, признак ошибки только `status: 0` в теле. По REST ожидаются 4xx. В Swagger для `GET /student/{id}` это описано («данные студента или сообщение об ошибке»), для остальных методов нет. Тест: `test_get_student_by_invalid_id`.
2. **Swagger: `host: localhost:8000`.** Кнопка «Try it out» отправляет запросы на `localhost`, а не на стенд, и завершается `TypeError: Failed to fetch`.
3. **Валидация `email`, `phone_no`, `name` отсутствует** (указано в описании API) при том, что схема объявляет `format: email`. В данных стенда есть записи с пустым email, `"not-an-email"`, телефоном `"abc"`. Тесты на валидацию этих полей не пишутся.
4. **Дубликаты принимаются.** В данных стенда есть студенты с одинаковым email (например, `dup@example.com`, id 65 и 66).