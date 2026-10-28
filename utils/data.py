import uuid


def build_student():
    unique_suffix = uuid.uuid4().hex[:8]

    return {
        "name": f"Test_Student_{unique_suffix}",
        "email": f"qa_{unique_suffix}@example.com",
        "phone_no": f"+7{unique_suffix[:10]}",
        "gender": "male",
        "status": 1
    }