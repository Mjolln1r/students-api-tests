[![API tests](https://github.com/Mjolln1r/students-api-tests/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Mjolln1r/students-api-tests/actions/workflows/tests.yml)
# Students API: автотесты

Автотесты для блока «students» (GET, POST, PUT, DELETE) по описанию из Swagger: `http://194.87.126.16/apidocs`.

**Стек:** Python 3.10+, pytest, requests, allure-pytest.

## Структура проекта

```
api/
  client.py            # ApiClient: один метод request() с шагом Allure, логом и вложениями
  students.py          # StudentsApi: get_students, get_student_by_id, create_student, update_student, delete_student
tests/
  conftest.py          # фикстуры: лог теста в Allure, клиент, created_student, create_student
  test_get_students.py
  test_post_students.py
  test_put_students.py
  test_delete_students.py
utils/
  check_schema.py      # проверка структуры и типов полей студента
  checks.py            # проверки, оформленные как шаги Allure
  data.py              # генерация тестовых данных
  logger.py            # лог каждого теста в отдельный файл
  wait.py              # wait_until: повтор запроса с таймаутом
config.py              # BASE_URL, TIMEOUT
pytest.ini
requirements.txt
bugs.md                # найденные баги
```

## Установка

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```bash
pytest                                     # все тесты
pytest tests/test_post_students.py         # один файл
pytest -k "delete"                         # по имени
```

Адрес API и таймаут можно переопределить переменными окружения:

```bash
BASE_URL=http://localhost:8000 TIMEOUT=15 pytest
```

После прогона создаются:
- `allure-results/`: результаты для Allure (шаги, вложения запросов и ответов, лог теста);
- `logs/`: лог каждого теста отдельным файлом.

## Запуск в Docker

```bash
docker build -t students-api-tests .

mkdir -p docker-out/logs
docker run --rm \
  -v "$PWD/docker-out:/out" \
  -v "$PWD/docker-out/logs:/app/logs" \
  students-api-tests pytest --alluredir=/out/allure-results
```

Результаты Allure появятся в `docker-out/allure-results`, логи в `docker-out/logs`. Отчёт: `allure serve docker-out/allure-results`.

Адрес API можно сменить: добавьте в `docker run` параметр `-e BASE_URL=http://host:port`.

Код возврата контейнера ненулевой, если есть красные тесты (это известные баги, см. [bugs.md](bugs.md)).

## Allure-отчёт

Нужен [Allure Commandline](https://allurereport.org/docs/install/) (на macOS: `brew install allure`).

```bash
allure serve allure-results                                # открыть отчёт в браузере
allure generate allure-results -o allure-report --clean    # собрать статический отчёт
```

В каждом тесте:
- **шаги:** на каждый запрос (`GET /student`, `POST /student`, ...) и на каждую проверку;
- **вложения:** `Response` (и `Request body`, если есть тело) на каждый запрос;
- **лог:** вложение `test.log` с полным логом теста (находится в блоке Tear down);
- **ссылки на баги:** у тестов, которые воспроизводят баг, в блоке Links указан его номер из `bugs.md`.
## CI

Тесты запускаются в GitHub Actions при каждом пуше в `main` и при pull request (файл `.github/workflows/tests.yml`). Результаты Allure и логи сохраняются как артефакты запуска (вкладка **Actions** → нужный запуск → **Artifacts**). Скачанную папку `allure-results` можно открыть командой `allure serve <папка>`.

CI всегда зелёный: красные тесты это известные баги API (см. [bugs.md](bugs.md)), а не поломка фреймворка. Для этого в workflow у шага с тестами стоит `continue-on-error: true`. Реальный результат прогона смотрите в артефактах и в логе шага `Run tests`.
## Покрытие

Всего 36 прогонов (с учётом параметризации).

| Метод | Проверки |
|---|---|
| GET | список и структура студента; студент по id; несуществующий id (тело и HTTP-код); нечисловой id (код и формат ответа); стабильность чтения; неактивный студент |
| POST | валидное создание и чтение обратно; допустимые значения `gender` и `status`; отсутствие каждого обязательного поля; недопустимые значения (`gender`, `status`); пустой JSON |
| PUT | обновление и проверка ответа; тип `status` в ответе; сохранение изменений (проверка через GET); `phone_no` не меняется; несуществующий id; отсутствие обязательных полей; недопустимые значения |
| DELETE | удаление и исчезновение студента; повторное удаление; несуществующий id; удалённый студент не возвращается |

### Техники тест-дизайна

| Техника | Где применена |
|---|---|
| Классы эквивалентности | валидные и невалидные `gender`, `status`, id (существующий, несуществующий, нечисловой) |
| Граничные значения | `status`: 0 и 1 допустимы, -1 и 2 нет; типы значений (`"1"` вместо `1`) |
| Таблица решений (обязательные поля) | отсутствие каждого из полей в POST и PUT, по одному прогону на поле |
| Переходы состояний (жизненный цикл) | создание → чтение → обновление → чтение → удаление → чтение; повторное удаление |
| Предположение об ошибках | пустой JSON, повторное удаление, нечисловой id |
| Проверка по спецификации | тип `status`, `phone_no` не обновляется через PUT, формат ошибки |

## Результат прогона и найденные баги

Часть тестов **намеренно красная**: они воспроизводят найденные дефекты API (подробности и шаги воспроизведения в [bugs.md](bugs.md)), это не поломка фреймворка.

| Тест | Баг |
|---|---|
| `test_get_student_is_consistent` | BUG-001: нестабильное чтение |
| `test_deleted_student_is_not_returned` | BUG-002: удалённый студент возвращается |
| `test_delete_twice`, `test_delete_nonexistent_student` | BUG-003: DELETE несуществующего возвращает success |
| `test_non_numeric_id_returns_json` | BUG-004: HTML вместо JSON |
| `test_update_is_persisted` | BUG-005: PUT не сохраняет gender |
| `test_update_student_status_type` | BUG-006: PUT возвращает status строкой |
| `test_get_inactive_student` | BUG-007: status в GET повторяет статус студента |
| `test_get_student_by_invalid_id` | NOTE-01: HTTP 200 вместо 404 |

## Особенности стенда

- **Нестабильное чтение (BUG-001).** Запросы по id иногда возвращают «Student not found» для существующего студента, а `PUT` иногда отвечает «not found, student not updated». Поэтому в положительных тестах используется `wait_until` (повтор запроса до успеха, не дольше 10 секунд), а отдельные тесты на сам баг повторов не используют. Все попытки видны в логе и в Allure.
- **Общий стенд.** На стенде есть чужие данные: тесты создают студентов с уникальными email и телефоном и сами удаляют только их (по id из ответа). Тесты не опираются на размер списка. Из-за BUG-001/002 удаление может быть неполным, поэтому на стенде возможны остатки тестовых данных.
- **Формат ответов.** Все ответы, включая ошибки, приходят с HTTP 200: успех или ошибка определяются полем `status` в теле. Исключение: нечисловой id (HTML 404 от веб-сервера).

## Что не покрыто

- Валидация `email`, `phone_no`, `name`: по описанию API она не предусмотрена (и при этом схема объявляет `format: email`, см. замечания в `bugs.md`).
- Проверка граничных значений id по `int32` и нагрузочные сценарии.
- Спецсимволы, длинные строки, заголовки запроса (`Content-Type`).