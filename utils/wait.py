import time


def wait_until(func, check, timeout=10, interval=0.5):
    """Повторять func(), пока check(результат) не станет True, но не дольше timeout секунд.
    Возвращает последний ответ."""
    deadline = time.time() + timeout
    result = func()
    while not check(result) and time.time() < deadline:
        time.sleep(interval)
        result = func()
    return result