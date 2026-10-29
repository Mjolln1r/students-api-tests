import allure

from utils.checks import check_body_status, check_message, check_status_code
from utils.wait import wait_until


@allure.feature("Студенты")
@allure.story("DELETE: удаление студента")
class TestDeleteStudents:

    @allure.title("DELETE /student/{id}: успешное удаление студента")
    def test_delete_student(self, students_api, created_student):
        sid = created_student["id"]

        response = students_api.delete_student(sid)

        check_status_code(response, expected=200)
        body = response.json()
        check_body_status(body, expected=1)
        check_message(body, expected="Student deleted successfully")
        after = wait_until(
            lambda: students_api.get_student_by_id(sid),
            lambda r: "student" not in r.json(),
        )
        assert "student" not in after.json(), f"Студент {sid} вернулся после удаления"

    @allure.issue("BUG-003", "DELETE несуществующего/повторное возвращает success")
    @allure.title("DELETE /student/{id}: повторное удаление")
    def test_delete_twice(self, students_api, created_student):
        sid = created_student["id"]
        check_status_code(students_api.delete_student(sid), expected=200)

        response = students_api.delete_student(sid)

        body = response.json()
        check_body_status(body, expected=0)
        check_message(body, expected="Student not found")

    @allure.issue("BUG-003", "DELETE несуществующего/повторное возвращает success")
    @allure.title("DELETE /student/{id}: несуществующий id")
    def test_delete_nonexistent_student(self, students_api):
        response = students_api.delete_student(999999)

        check_status_code(response, expected=404)
        body = response.json()
        check_body_status(body, expected=0)
        check_message(body, expected="Student not found")

    @allure.issue("BUG-002", "Удалённый студент возвращается через GET")
    @allure.title("DELETE /student/{id}: удалённый студент не возвращается через GET")
    def test_deleted_student_is_not_returned(self, students_api, created_student):
        sid = created_student["id"]
        check_status_code(students_api.delete_student(sid), expected=200)

        found = ["student" in students_api.get_student_by_id(sid).json() for _ in range(10)]

        assert not any(found), f"Удалённый студент вернулся в {sum(found)} из 10 ответов"
