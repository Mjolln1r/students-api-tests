import pytest

from utils.checks import check_status_code, check_body_status, check_message
from utils.data import build_student


@pytest.mark.xfail(reason="BUG-001: GET /student/{id} нестабилен после создания", strict=False)
def test_get_student_is_consistent(self, students_api):
    student = students_api.create_student(build_student()).json()["student"]
    try:
        statuses = [students_api.get_student_by_id(student["id"]).json()["status"] for _ in range(10)]
        assert statuses == [1] * 10, f"Нестабильные ответы: {statuses}"
    finally:
        students_api.delete_student(student["id"])

@pytest.mark.xfail(reason="BUG-002: API возвращает HTTP 200 вместо 404 для несуществующего студента")
def test_get_student_by_invalid_id(students_api, created_student):
    response = students_api.get_student_by_id(999999)

    check_status_code(response, expected=404)
    body = response.json()
    check_body_status(body=body, expected=0)
    check_message(body=body, expected="Student not found")


@pytest.mark.xfail(reason="BUG-003: DELETE несуществующего студента возвращает success", strict=False)
@allure.title("DELETE /student/{id}: несуществующий id")
def test_delete_nonexistent_student(self, students_api):
    response = students_api.delete_student(999999)

    check_status_code(response, expected=200)
    body = response.json()
    check_body_status(body, expected=0)
    check_message(body, expected="Student not found")