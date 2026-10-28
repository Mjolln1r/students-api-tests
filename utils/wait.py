import time

def wait_for_status(api, student_id, expected_status, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            res = api.get_student_by_id(student_id)
            if res.json().get("status") == expected_status:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False