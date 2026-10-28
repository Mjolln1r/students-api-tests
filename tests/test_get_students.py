import pytest
import allure
from utils.check_schema import check_student_schema
from utils.wait import wait_until
from utils.data import build_student


@allure.feature("Студенты")
@allure.story("GET: Получение студентов")
class TestGetStudents:
    @allure.title("GET /student: список студента и структура каждого")
    def test_get_students(self, students_api):
        response = students_api.get_students()
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == 1
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
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == 1
        check_student_schema(payload["student"])
        assert payload["student"] == created_student

    @pytest.mark.xfail(reason="BUG-001: GET /student/{id} нестабилен после создания", strict=False)
    def test_get_student_is_consistent(students_api):
        student = students_api.create_student(build_student()).json()["student"]
        try:
            statuses = [students_api.get_student_by_id(student["id"]).json()["status"] for _ in range(10)]
            assert statuses == [1] * 10, f"Нестабильные ответы: {statuses}"
        finally:
            students_api.delete_student(student["id"])
