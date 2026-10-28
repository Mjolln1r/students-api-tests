import pytest
import allure
from utils.check_schema import check_student_schema
from utils.wait import wait_until
from utils.data import build_student
from utils.checks import check_status_code, check_body_status, check_student_fields, check_message


@allure.feature("Студенты")
@allure.story("GET: Получение студентов")
class TestGetStudents:
    @allure.title("GET /student: список студента и структура каждого")
    def test_get_students(self, students_api):
        response = students_api.get_students()

        check_status_code(response, expected=200)
        payload = response.json()
        check_body_status(payload, expected=1)
        assert isinstance(payload["students"], list)
        for student in payload["students"]:
            check_student_schema(student)

    @allure.title("GET student/{id}: студент по существующему id")
    def test_get_student_by_id(self, students_api, created_student):
        sid = created_student["id"]
        response = wait_until(
            lambda: students_api.get_student_by_id(sid),
            lambda r: r.json()["status"] == 1,
        )

        check_status_code(response, expected=200)
        payload = response.json()
        check_body_status(payload, expected=1)
        check_student_schema(payload["student"])
        check_student_fields(payload["student"], created_student)

    @pytest.mark.xfail(reason="Замечание: API возвращает HTTP 200 вместо 404 для несуществующего студента")
    @allure.title("GET student/{id}: студент по несуществующему id")
    def test_get_student_by_invalid_id(self, students_api):
        response = students_api.get_student_by_id(999999)

        check_status_code(response, expected=404)
        body = response.json()
        check_body_status(body=body, expected=0)
        check_message(body=body, expected="Student not found")

    @allure.title("GET student/{id}: студент с нечисловым id")
    def test_get_student_with_non_numeric_id(self, students_api):
        response = students_api.get_student_by_id("abc")

        check_status_code(response=response, expected=404)
