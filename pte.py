# Import standard libraries
import importlib
import json
import logging
import os
import time

# Import 3rd-party libraries
import structlog



# Define parameters
_scanRun = False
_dryRun = False

_stateFile = None
_stateTime = -1

_startTime = -1
_endTime = -1

_increasingTotal = True
_totalTestSuites = 0
_totalTests = 0

_passedTestSuites = 0
_failedTestSuites = 0
_skippedTestSuites = 0
_passedTests = 0
_failedTests = 0
_skippedTests = 0



# Define variables
logger = None

shared = {}



def _initLogger():
    global logger
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
    logger = structlog.get_logger()



def run(testPath = 'tests', runPath = 'tests', dryRun = False, scanRun = True, stateFile = None):

    global _stateFile, _startTime, _endTime, _scanRun, _dryRun, _increasingTotal
    global _skippedTestSuites, _passedTestSuites, _failedTestSuites, _skippedTests, _passedTests, _failedTests

    # Save the parameters
    _stateFile = stateFile

    # Set the parameters
    _startTime = time.time()

    # Initialize the logger
    _initLogger()

    # Scan
    if scanRun:
        _scanRun = True
        _dryRun = True
        _runPath(testPath, runPath)

    # Run
    _scanRun = False
    _dryRun = dryRun
    _increasingTotal = not scanRun

    _passedTestSuites = 0
    _failedTestSuites = 0
    _skippedTestSuites = 0
    _passedTests = 0
    _failedTests = 0
    _skippedTests = 0
        
    _runPath(testPath, runPath)

    # Stop and write final state file
    _endTime = time.time()
    _writeState(False)



def _runPath(testPath, runPath):
    logger.debug("Searching test suite in: %s", testPath)

    testUnderRun = testPath == runPath or testPath.startswith(runPath + os.sep)
    runUnderTest = testPath == runPath or runPath.startswith(testPath + os.sep)

    if not (testUnderRun or runUnderTest):
        return
    ifrun = testUnderRun

    if os.path.isfile(testPath + '/_initialize.py'):
        _runFile(testPath + '/_initialize.py')

    with os.scandir(testPath) as it:
        fd = list(it)
        fd.sort(key=lambda e: e.name)

    for entry in fd:
        if entry.name.startswith('_'):
            continue
        if not entry.is_file():
            _runPath(entry.path, runPath)
        elif ifrun and entry.name.endswith('.py'):
            _runFile(entry.path)

    if os.path.isfile(testPath + '/_uninitialize.py'):
        _runFile(testPath + '/_uninitialize.py')



def _runFile(testFile):

    moduleName = testFile[:-3].replace('/', '.')
    logger.debug("Processing test suite: %s", moduleName)
    module = importlib.import_module(moduleName)
    module.run()
    logger.debug("Processed test suite %s", moduleName)

    if time.time() - _stateTime > 10:
        _writeState(True)



def _writeState(isRunning = True):
    global _stateTime

    data = {
        "isRunning": isRunning, "startTime": _startTime, "endTime": _endTime, "stateTime": _stateTime,
        "totalTestSuites": _totalTestSuites, "totalTests": _totalTests,
        "passedTestSuites": _passedTestSuites, "failedTestSuites": _failedTestSuites, "skippedTestSuites": _skippedTestSuites,
        "passedTests": _passedTests, "failedTests": _failedTests, "skippedTests": _skippedTests
    }

    _stateTime = time.time()
    if _stateFile is not None:
        with open(_stateFile, 'w') as f:
            json.dump(data, f)
    logger.debug("State: ", **data)
    if not isRunning:
        logger.info("")
        logger.info("")
        logger.info("======================================================")
        logger.info("Total time: %.2f seconds.", _endTime - _startTime)
        if _failedTests > 0:
            logger.error("Failed tests: %u / %u.", _failedTests, _totalTests)
            logger.error("Failed test suites: %u / %u.", _failedTestSuites, _totalTestSuites)
        else:
            logger.info("Failed tests: %u / %u.", _failedTests, _totalTests)
            logger.info("Failed test suites: %u / %u.", _failedTestSuites, _totalTestSuites)
        logger.info("======================================================")



class PteTestSuite:

    def __init__(self, name, skip = False):
        global _totalTestSuites

        self.name = name
        self.skip = skip

        if _increasingTotal:
            _totalTestSuites += 1

        self.tests = []
        self.passedTests = 0
        self.failedTests = 0
        self.skippedTests = 0

    def initialize(self):
        logger.debug("Test suite %s initialized.", self.name)

    def uninitialize(self):
        logger.debug("Test suite %s uninitialized.", self.name)

    def run(self):
        global _skippedTestSuites, _passedTestSuites, _failedTestSuites, _skippedTests, _passedTests, _failedTests

        if self.skip:
            _skippedTestSuites += 1
            if not _scanRun:
                logger.info("======================================================")
                logger.info("[SKIP ] Test suite: %s.", self.name)
                logger.info("======================================================")
                logger.info("")
            return
        
        if not _dryRun:
            self.initialize()
        
        if not _scanRun:
            logger.info("")
            logger.info("======================================================")
        i = 1
        for test in self.tests:
            if not _scanRun:
                logger.info("[START] Test: %s (%u / %u tests).", test.name, i, len(self.tests))
            result = test._run()
            if result is None:
                _skippedTests += 1
                self.skippedTests += 1
                if not _scanRun:
                    logger.info("[SKIP ] Test: %s (%u / %u tests).", test.name, i, len(self.tests))
            elif result == True:
                _passedTests += 1
                self.passedTests += 1
                if not _scanRun:
                    logger.info("[OKAY ] Test: %s (%u / %u tests).", test.name, i, len(self.tests))
            else:
                _failedTests += 1
                self.failedTests += 1
                if not _scanRun:
                    logger.error("[ERROR] Test: %s (%u / %u tests).", test.name, i, len(self.tests))
            i += 1

        if not _dryRun:
            self.uninitialize()

        if self.failedTests == 0:
            _passedTestSuites += 1
            if not _scanRun:
                logger.info("======================================================")
                logger.info("[OKAY ] Test suite: %s (%u tests).", self.name, len(self.tests))
                logger.info("======================================================")
                logger.info("")
        else:
            _failedTestSuites += 1
            if not _scanRun:
                logger.error("======================================================")
                logger.error("[ERROR] Test suite: %s (%u tests).", self.name, len(self.tests))
                logger.error("======================================================")
                logger.error("")



class PteTest:
    
    def __init__(self, testSuite, name, skip = False, fun = None):
        global _totalTests
        
        self.name = name
        self.skip = skip
        self.testSuite = testSuite
        self.fun = None
        testSuite.tests.append(self)
        
        if _increasingTotal:
            _totalTests += 1

    def _run(self):
        if self.skip:
            return None
        if _dryRun:
            return True
        return self.execute()

    def execute(self):
        if self.fun is None:
            return None
        return self.fun()