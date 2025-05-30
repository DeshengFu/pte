# Import standard libraries
import json
import requests
import os

# Import own libraries
import pte



class PteRestBasicTest(pte.PteTest):
    
    def __init__(self, testSuite, name, skip = False, fun = None, url = "http://localhost/", method = "get", headers = {}, cookies = {}, data = None, expCode = 200, expText = '', timeout = 0.01):
        super().__init__(testSuite, name, skip, fun)
        self.url = url
        self.method = method
        self.headers = headers
        self.cookies = cookies
        self.data = data
        self.expCode = expCode
        self.expText = expText
        self.timeout = timeout
        self.response = None

    def execute(self):
        try:
            self.response = requests.request(self.method, self.url, headers=self.headers, data=self.data, cookies=self.cookies, timeout=self.timeout)
        except Exception as e:
             pte.logger.error("  * %s.", repr(e))
             return False
        if self.response.status_code != self.expCode:
            pte.logger.error("  Invalid status code.")
            pte.logger.error("  Expected: %u.", self.expCode)
            pte.logger.error("  Received: %u.", self.response.status_code)
            return False
        if self.expCode < 200 or self.expCode > 299:
            return True
        if not self.compareText(self.response.text, self.expText):
            pte.logger.error("  Invalid response.")
            pte.logger.error("  Expected: \n%s.", self.expText)
            pte.logger.error("  Received: \n%s.", self.response.text)
            return False
        return True

    def compareText(self, text1, text2):
        return text1 == text2



class PteRestJsonTest(PteRestBasicTest):
    
    def __init__(self, testSuite, name, skip = False, fun = None, url = "http://localhost/", method = "get", headers = {}, cookies = {}, data = {}, expCode = 200, expJSON = {}, timeout = 0.01):
        super().__init__(testSuite, name, skip, fun, url, method, headers, cookies, json.dumps(data), expCode, json.dumps(expJSON), timeout)

    def compareText(self, text1, text2):
        text1Json = json.loads(text1)
        text2Json = json.loads(text2)
        return PteRestJsonTest._ordered(text1Json) == PteRestJsonTest._ordered(text2Json)

    @staticmethod
    def _ordered(obj):
        if isinstance(obj, dict):
            return sorted((k, PteRestJsonTest._ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(PteRestJsonTest._ordered(x) for x in obj)
        else:
            return obj



class PteRestJsonFileTest(PteRestJsonTest):
    
    def __init__(self, testSuite, name, skip = False, fun = None, url = "http://localhost/", method = "get", headers = {}, cookies = {}, data = {}, expCode = 200, scriptPath = "", expJSON = "", timeout = 0.01):
        d = {}
        path = os.path.abspath(os.path.dirname(scriptPath) + expJSON)
        with open(path) as f:
            d = json.load(f)
        super().__init__(testSuite, name, skip, fun, url, method, headers, cookies, json.dumps(data), expCode, d, timeout)
