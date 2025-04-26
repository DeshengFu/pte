import pte
import pterest

class TestSuite(pte.PteTestSuite):
    def __init__(self):
        super().__init__("Rest Test Suite")
testSuite = TestSuite()
def run():
    testSuite.run()

test1 = pterest.PteRestJsonTest(testSuite, "JSON Test", url="http://localhost/", method="get", expJSON='')