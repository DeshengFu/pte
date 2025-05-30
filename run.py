# Import standard libraries
import sys

# Import own libraries
import pte



dryRun = False
scanRun = True
testPath = 'tests'
runPath = None
stateFile = None
for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    if arg == '-d' or arg == '--dry-run':
        dryRun = True
    elif arg == '-ns' or arg == '--no-scan':
        scanRun = False
    elif (arg == '-rp' or arg == '--run-path') and i + 1 < len(sys.argv):
        runPath = sys.argv[i + 1]
    elif (arg == '-tp' or arg == '--test-path') and i + 1 < len(sys.argv):
        testPath = sys.argv[i + 1]
    elif (arg == '-s' or arg == '--state-file') and i + 1 < len(sys.argv):
        stateFile = sys.argv[i + 1]
if runPath is None:
    runPath = testPath

pte.run(testPath, runPath, dryRun, scanRun, stateFile)
