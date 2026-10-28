import allure


@allure.feature("Students API")
@allure.story("Удаление студента")
class TestDeleteStudents:
    @allure.title("DELETE student/{id}: успешное удаление студента")
    def test_delete_student(self, students_api, created_student):
        student_id = created_student["id"]
        delete_response = students_api.delete_student(student_id)
        assert delete_response.status_code == 200
        assert delete_response.json().get("status") == 1
        get_response = students_api.get_student_by_id(student_id)
        # Если API возвращает 200 OK и status: 1 — значит, удаление не сработало!
        assert get_response.status_code == 404 or get_response.json().get("status") == 0, \
            f"БАГ: Студент {student_id} вернулся в GET после успешного DELETE"
