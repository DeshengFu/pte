import pte
import pterest
import ptescript

class TestSuite(pte.PteTestSuite):
    def __init__(self):
        super().__init__("Uninitialize")
testSuite = TestSuite()
def run():
    testSuite.run()

class Uninit1(pte.PteTest):
    def __init__(self):
        super().__init__(testSuite, "Uninitialize Step 1")

    def execute(self):
        ptescript.run("config.json", "uninitCmd")
        return True
Uninit1()