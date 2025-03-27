import pte

class TestSuite(pte.PteTestSuite):
    def __init__(self):
        super().__init__("Basic Test Suite")
testSuite = TestSuite()
def run():
    testSuite.run()

class Test1(pte.PteTest):
    def __init__(self):
        super().__init__(testSuite, "Hello World Test")

    def execute(self):
        pte.logger.info("  * Say \"Hello World\" and return okay")
        return True
Test1()