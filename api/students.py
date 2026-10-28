from api.client import ApiClient


class StudentsApi:
    def __init__(self, client: ApiClient):
        self.client = client


    def get_students(self):
        return self.client.request(method="GET", path="/student")


    def get_student_by_id(self, student_id):
        return self.client.request(method="GET", path=f"/student/{student_id}")


    def create_student(self, payload):
        return self.client.request(method="POST", path="/student", json=payload)


    def update_student(self, payload, student_id):
        return self.client.request(method="PUT", path=f"/student/{student_id}", json=payload)


    def delete_student(self, student_id):
        return self.client.request(method="DELETE", path=f"/student/{student_id}")