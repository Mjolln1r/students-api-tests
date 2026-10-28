import logging


def test_get_students(students_api):
    log = logging.getLogger("student_api")
    print(log.level, log.handlers)
    log.info("проверка записи в лог")
    response = students_api.get_students()
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == 1
