


def test_get_students(students_api):
    response = students_api.get_students()
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == 1