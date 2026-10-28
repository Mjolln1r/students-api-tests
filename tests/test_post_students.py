import allure
import pytest

from utils.check_schema import check_student_schema
from utils.checks import check_status_code, check_body_status, check_message, check_student_fields, \
    check_message_contains
from utils.data import build_student
from utils.wait import wait_until

REQUIRED_FIELDS = ["name", "email", "phone_no", "gender", "status"]


@allure.feature("Студенты")
@allure.story("POST: создание студента")
class TestCreateStudent:

    @allure.title("POST /student: валидное создание и сохранение")
    def test_create_student(self, students_api, create_student):
        payload = build_student()

        response = create_student(payload)

        check_status_code(response, expected=200)
        body = response.json()
        check_body_status(body, expected=1)
        check_message(body, expected="Student created successfully")
        check_student_schema(body["student"])
        check_student_fields(body["student"], payload)

        sid = body["student"]["id"]
        found = wait_until(
            lambda: students_api.get_student_by_id(sid),
            lambda r: r.json()["status"] == 1,
        )
        check_body_status(found.json(), expected=1)
        check_student_fields(found.json()["student"], payload)

    @pytest.mark.parametrize("gender, status", [("male", 0), ("female", 1)])
    @allure.title("POST /student: допустимые значения gender={gender}, status={status}")
    def test_create_student_valid_enum_values(self, create_student, gender, status):
        payload = build_student(gender=gender, status=status)

        response = create_student(payload)
        check_status_code(response, expected=200)
        body = response.json()
        check_body_status(body, expected=1)
        check_message(body, expected="Student created successfully")
        check_student_fields(body["student"], payload)

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    @allure.title("POST /student: нет обязательного поля {field}")
    def test_create_student_without_required_field(self, create_student, field):
        payload = build_student()
        payload.pop(field)

        response = create_student(payload)

        body = response.json()
        check_body_status(body, expected=0)
        check_message(body, expected="Wrong JSON, student not created")

    @pytest.mark.parametrize("field, value", [
        ("gender", "other"),
        ("status", 2),
        ("status", -1),
        ("status", "1"),
    ])
    @allure.title("POST /student: недопустимое значение {field}={value}")
    def test_create_student_invalid_value(self, create_student, field, value):
        response = create_student(build_student(**{field: value}))

        body = response.json()
        check_body_status(body, expected=0)
        check_message_contains(body, fragment="not created")

    @allure.title("POST /student: пустой JSON")
    def test_create_student_empty_json(self, create_student):
        response = create_student({})

        body = response.json()
        check_body_status(body, expected=0)
        check_message(body, expected="Empty JSON, student not created")
