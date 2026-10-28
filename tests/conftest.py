import pytest
from api.students import StudentsApi
from api.client import ApiClient
from utils.data import build_student


@pytest.fixture(scope="session")
def students_api():
    return StudentsApi(ApiClient())


@pytest.fixture
def created_student(students_api):
    response = students_api.create_student(build_student())
    student = response.json()["student"]
    yield student
    students_api.delete_student(student["id"])
