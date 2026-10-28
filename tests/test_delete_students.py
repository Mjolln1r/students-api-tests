import allure

from utils.wait import wait_until


@allure.feature("Students API")
@allure.story("Удаление студента")
class TestDeleteStudents:
    @allure.title("DELETE student/{id}: успешное удаление студента")
    def test_delete_student(self, students_api, created_student):
        sid = created_student["id"]

        response = students_api.delete_student(sid)

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 1
        assert body["message"] == "Student deleted successfully"
        after = wait_until(
            lambda: students_api.get_student_by_id(sid),
            lambda r: r.json()["status"] == 0,
        )
        assert after.json()["status"] == 0, f"Студент {sid} не исчез после удаления"
