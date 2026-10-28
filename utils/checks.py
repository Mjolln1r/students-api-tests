import allure


@allure.step("Проверить код ответа: {expected}")
def check_status_code(response, expected):
    assert response.status_code == expected, (
        f"Ожидался код {expected}, получен {response.status_code}. Тело: {response.text[:300]}"
    )


@allure.step("Проверить поле status в теле: {expected}")
def check_body_status(body, expected):
    assert body["status"] == expected, f"Ожидался status={expected}, тело: {body}"


@allure.step("Проверить сообщение: {expected}")
def check_message(body, expected):
    assert body["message"] == expected, f"Ожидалось {expected!r}, получено {body['message']!r}"


@allure.step("Сверить поля студента с ожидаемыми")
def check_student_fields(student, expected):
    for key, value in expected.items():
        assert student[key] == value, f"Поле {key}: ожидалось {value!r}, получено {student[key]!r}"


@allure.step("Проверить, что сообщение содержит: {fragment}")
def check_message_contains(body, fragment):
    assert fragment in body["message"], f"В сообщении {body['message']!r} нет {fragment!r}"
