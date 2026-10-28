import time
import pytest
import allure
from utils.check_schema import check_student_schema
from utils.wait import wait_for_status


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


    @pytest.mark.xfail(
        reason="Баг API: GET по ID нестабилен из-за кэша/балансировщика. Возвращает status:0 для только что созданных студентов.")
    @allure.title("GET student/{id}: студент по существующему id")
    def test_get_student_by_id(self, students_api, created_student):
        student_id = created_student["id"]
        is_found = wait_for_status(students_api, student_id, expected_status=1)
        assert is_found, f"Сервер не отдает студента {student_id}"
        response = students_api.get_student_by_id(student_id)
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == 1
        check_student_schema(payload["student"])
        assert payload["student"] == created_student
