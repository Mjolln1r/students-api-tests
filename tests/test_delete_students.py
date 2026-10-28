import allure
import pytest

from utils.checks import check_status_code, check_body_status, check_message
from utils.wait import wait_until


@allure.feature("Студенты")
@allure.story("DELETE: удаление студента")
class TestDeleteStudents:

    @allure.title("DELETE /student/{id}: успешное удаление студента")
    def test_delete_student(self, students_api, created_student):
        sid = created_student["id"]

        response = students_api.delete_student(sid)

        check_status_code(response=response, expected=200)
        body = response.json()
        check_body_status(body=body, expected=1)
        check_message(body=body, expected="Student deleted successfully")
        after = wait_until(
            lambda: students_api.get_student_by_id(sid),
            lambda r: r.json()["status"] == 0,
        )
        check_body_status(after.json(), expected=0)

    @pytest.mark.xfail(reason="BUG-003: DELETE несуществующего студента возвращает success", strict=False)
    @allure.title("DELETE /student/{id}: несуществующий id")
    def test_delete_nonexistent_student(self, students_api):
        response = students_api.delete_student(999999)

        check_status_code(response=response, expected=404)
        body = response.json()
        check_body_status(body=body, expected=0)
        check_message(body=body, expected="Student not found")

    def test_probe_delete_twice(self, students_api, created_student):
        sid = created_student["id"]
        print("first:", students_api.delete_student(sid).text)
        print("second:", students_api.delete_student(sid).text)