import allure

STUDENT_FIELDS = {"id", "name", "email", "phone_no", "gender", "status"}

def check_student_schema(student):
    with allure.step("Проверка структуры и типов данных полей"):
        missing = STUDENT_FIELDS - set(student)
        assert not missing, f"В ответе нет полей: {sorted(missing)}"
        assert isinstance(student["id"], int), f"id not int: {student["id"]}"
        assert isinstance(student["name"], str), f"name not str: {student["name"]}"
        assert isinstance(student["email"], str), f"email not str: {student["email"]}"
        assert isinstance(student["phone_no"], str), f"phone not str: {student["phone_no"]}"
        assert student["gender"] in ("male", "female"), f"gender: {student["gender"]}"
        assert student["status"] in (0, 1), f"status: {student["status"]}"