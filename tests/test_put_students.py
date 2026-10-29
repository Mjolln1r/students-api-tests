import allure
import pytest

from utils.checks import check_body_status, check_message, check_status_code, check_student_fields
from utils.data import build_update
from utils.wait import wait_until


def update_until_ok(api, sid, payload):
    """PUT с повторами: из-за BUG-001 запрос иногда попадает на экземпляр, где студента нет."""
    return wait_until(
        lambda: api.update_student(sid, payload),
        lambda r: r.json()["status"] == 1,
    )


@allure.feature("Студенты")
@allure.story("PUT: обновление студента")
class TestUpdateStudent:

    @allure.title("PUT /student/{id}: обновление имени, email и gender")
    def test_update_student(self, students_api, created_student):
        payload = build_update()

        response = update_until_ok(students_api, created_student["id"], payload)

        check_status_code(response, expected=200)
        body = response.json()
        check_body_status(body, expected=1)
        check_message(body, expected="Student updated successfully")
        check_student_fields(body["student"], {k: payload[k] for k in ("name", "email", "gender")})

    @allure.issue("BUG-006", "PUT возвращает status строкой")
    @allure.title("PUT /student/{id}: status в ответе число")
    def test_update_student_status_type(self, students_api, created_student):
        response = update_until_ok(students_api, created_student["id"], build_update(status=0))

        status = response.json()["student"]["status"]
        assert isinstance(status, int), f"status пришёл как {type(status).__name__}: {status!r}"

    @allure.issue("BUG-005", "PUT не сохраняет gender")
    @allure.title("PUT /student/{id}: изменения сохраняются (проверка через GET)")
    def test_update_is_persisted(self, students_api, created_student):
        sid = created_student["id"]
        payload = build_update()
        update_until_ok(students_api, sid, payload)

        response = wait_until(
            lambda: students_api.get_student_by_id(sid),
            lambda r: r.json().get("student", {}).get("name") == payload["name"],
        )

        check_student_fields(response.json()["student"], payload)

    @allure.title("PUT /student/{id}: phone_no не меняется")
    def test_update_does_not_change_phone(self, students_api, created_student):
        payload = build_update(phone_no="+70000000000")

        response = update_until_ok(students_api, created_student["id"], payload)

        check_student_fields(response.json()["student"], {"phone_no": created_student["phone_no"]})

    @allure.title("PUT /student/{id}: несуществующий id")
    def test_update_nonexistent_student(self, students_api):
        response = students_api.update_student(999999, build_update())

        body = response.json()
        check_body_status(body, expected=0)
        check_message(body, expected="Student not found, student not updated")

    @pytest.mark.parametrize("field", ["name", "email", "gender", "status"])
    @allure.title("PUT /student/{id}: нет обязательного поля {field}")
    def test_update_without_required_field(self, students_api, created_student, field):
        payload = build_update()
        payload.pop(field)

        response = students_api.update_student(created_student["id"], payload)

        body = response.json()
        check_body_status(body, expected=0)
        check_message(body, expected="Wrong JSON, student not updated")

    @pytest.mark.parametrize("field, value, message", [
        ("gender", "other", "Wrong gender, student not updated"),
        ("status", 2, "Wrong status, student not updated"),
    ])
    @allure.title("PUT /student/{id}: недопустимое значение {field}={value}")
    def test_update_with_invalid_value(self, students_api, created_student, field, value, message):
        response = students_api.update_student(created_student["id"], build_update(**{field: value}))

        body = response.json()
        check_body_status(body, expected=0)
        check_message(body, expected=message)
