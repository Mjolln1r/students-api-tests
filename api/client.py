import logging

import requests
import config
import allure

log = logging.getLogger("student_api")


class ApiClient:
    def __init__(self, base_url=config.BASE_URL, timeout=config.TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        with allure.step(f"{method} {path}"):
            log.info("REQUEST %s %s %s", method, url, kwargs.get("json"))
            response = self.session.request(method, url, **kwargs)
            log.info("RESPONSE %s %s", response.status_code, response.text)
            allure.attach(response.text, name=f"Response {response.status_code}",
                          attachment_type=allure.attachment_type.JSON)
            return response
