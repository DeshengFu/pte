# Import standard libraries
import importlib
import json
import logging
import os
import requests
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



def _initLogger():
    global logger
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
    logger = structlog.get_logger()



def run(testPath = 'tests', dryRun = False, scanRun = True, stateFile = None):

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
        _runPath(testPath)

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
        
    _runPath(testPath)

    # Stop and write final state file
    _endTime = time.time()
    _writeState(False)



def _runPath(testPath):
    logger.debug("Searching test suite in: %s", testPath)

    with os.scandir(testPath) as it:
        for entry in it:
            if entry.name.startswith('_'):
                continue
            if not entry.is_file():
                _runPath(entry.path)
            elif entry.name.endswith('.py'):
                _runFile(entry.path)



def _runFile(testFile):

    moduleName = testFile[:-3].replace('/', '.')
    logger.debug("Processing test suite: %s", moduleName)
    module = importlib.import_module(moduleName)
    module.run()
    logger.debug("Processed test suite %s", moduleName)

    if time.time() - _stateTime > 1000:
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
                logger.info("[SKIP ] Test suite: %s.", self.name)
            return
        
        if not _dryRun:
            self.initialize()

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
                logger.info("[OKAY ] Test suite: %s (%u tests).", self.name, len(self.tests))
        else:
            _failedTestSuites += 1
            if not _scanRun:
                logger.info("[ERROR] Test suite: %s (%u tests).", self.name, len(self.tests))



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