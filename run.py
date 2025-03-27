# Import standard libraries
import sys

# Import own libraries
import pte



dryRun = False
scanRun = True
path = 'tests'
stateFile = None
for i in sys.argv[1:]:
    if sys.argv[i] == '-d' or sys.argv[i] == '--dry-run':
        dryRun = True
    elif sys.argv[i] == '-ns' or sys.argv[i] == '--no-scan':
        scanRun = False
    elif (sys.argv[i] == '-p' or sys.argv[i] == '--path') and i + 1 < len(sys.argv):
        path = sys.argv[i + 1]
    elif (sys.argv[i] == '-s' or sys.argv[i] == '--state-file') and i + 1 < len(sys.argv):
        stateFile = sys.argv[i + 1]

pte.run(path, dryRun, scanRun, stateFile)
