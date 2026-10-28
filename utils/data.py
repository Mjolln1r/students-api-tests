import uuid


def build_student(**overrides):
    """Валидное тело для POST /student. Любое поле можно переопределить."""
    payload = {
        "name": "Ivan Ivanov",
        "email": f"qa_{uuid.uuid4().hex[:10]}@example.com",
        "phone_no": "+7" + str(uuid.uuid4().int)[:10],
        "gender": "male",
        "status": 1,
    }
    payload.update(overrides)
    return payload