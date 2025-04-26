# Import standard libraries
import sys

# Import own libraries
import pte



dryRun = False
scanRun = True
path = 'tests'
stateFile = None
for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    if arg == '-d' or arg == '--dry-run':
        dryRun = True
    elif arg == '-ns' or arg == '--no-scan':
        scanRun = False
    elif (arg == '-p' or arg == '--path') and i + 1 < len(sys.argv):
        path = sys.argv[i + 1]
    elif (arg == '-s' or arg == '--state-file') and i + 1 < len(sys.argv):
        stateFile = sys.argv[i + 1]

pte.run(path, dryRun, scanRun, stateFile)
