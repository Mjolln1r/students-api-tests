import allure

from utils.check_schema import check_student_schema
from utils.checks import (
    check_message,
    check_body_status,
    check_status_code,
    check_student_fields,
)
from utils.data import build_student
from utils.wait import wait_until


@allure.feature("Студенты")
@allure.story("GET: Получение студентов")
class TestGetStudents:

    @allure.title("GET /student: список студентов и структура каждого")
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
            lambda r: "student" in r.json(),
        )

        check_status_code(response, expected=200)
        payload = response.json()
        check_body_status(payload, expected=1)
        check_student_schema(payload["student"])
        check_student_fields(payload["student"], created_student)

    @allure.title("GET student/{id}: несуществующий id, тело ответа")
    def test_get_nonexistent_student_body(self, students_api):
        response = students_api.get_student_by_id(999999)

        body = response.json()
        check_body_status(body, expected=0)
        check_message(body, expected="Student not found")

    @allure.issue("NOTE-01", "API возвращает HTTP 200 вместо 404 для несуществующего студента")
    @allure.title("GET student/{id}: несуществующий id, HTTP-код 404")
    def test_get_student_by_invalid_id(self, students_api):
        response = students_api.get_student_by_id(999999)

        check_status_code(response, expected=404)

    @allure.title("GET student/{id}: студент с нечисловым id")
    def test_get_student_with_non_numeric_id(self, students_api):
        response = students_api.get_student_by_id("abc")

        check_status_code(response, expected=404)

    @allure.issue("BUG-004", "На нечисловой id API возвращает HTML вместо JSON")
    @allure.title("GET student/abc: ошибка возвращается в формате JSON")
    def test_non_numeric_id_returns_json(self, students_api):
        response = students_api.get_student_by_id("abc")

        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Content-Type: {content_type}"

    @allure.issue("BUG-001", "GET /student/{id} нестабилен")
    @allure.title("GET student/{id}: ответы стабильны после создания")
    def test_get_student_is_consistent(self, students_api):
        student = students_api.create_student(build_student()).json()["student"]
        try:
            found = ["student" in students_api.get_student_by_id(student["id"]).json() for _ in range(10)]
            assert all(found), f"Студент найден в {sum(found)} из 10 запросов: {found}"
        finally:
            students_api.delete_student(student["id"])

    @allure.issue("BUG-007", "status в GET повторяет статус студента")
    @allure.title("GET student/{id}: найденный студент со status=0 возвращается с status=1")
    def test_get_inactive_student(self, students_api, create_student):
        sid = create_student(build_student(status=0)).json()["student"]["id"]
        response = wait_until(
            lambda: students_api.get_student_by_id(sid),
            lambda r: "student" in r.json(),
        )

        check_body_status(response.json(), expected=1)
