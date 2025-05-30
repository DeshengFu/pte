import pte
import pterest
import ptescript

class TestSuite(pte.PteTestSuite):
    def __init__(self):
        super().__init__("Initialize")
testSuite = TestSuite()
def run():
    testSuite.run()

class Init1(pte.PteTest):
    def __init__(self):
        super().__init__(testSuite, "Initialize Step 1")

    def execute(self):
        ptescript.run("config.json", "initCmd")
        return True
Init1()