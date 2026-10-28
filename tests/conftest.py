import pytest
from api.students import StudentsApi
from api.client import ApiClient
from utils.data import build_student
import allure
from utils.logger import start_test_log, stop_test_log


@pytest.fixture(autouse=True)
def test_log(request):
    """Лог каждого теста пишется в свой файл и прикрепляется к тесту в Allure."""
    handler, path = start_test_log(request.node.nodeid)
    yield
    stop_test_log(handler)
    allure.attach.file(str(path), name="test.log",
                       attachment_type=allure.attachment_type.TEXT)


@pytest.fixture(scope="session")
def students_api():
    return StudentsApi(ApiClient())


@pytest.fixture
def created_student(students_api):
    response = students_api.create_student(build_student())
    student = response.json()["student"]
    yield student
    students_api.delete_student(student["id"])
