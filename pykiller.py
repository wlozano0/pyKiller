import datetime
import time
import os
import operator

CHECK_LINE = 'Error: 1034 for'
KILL = True

CHECK_LIMIT_VALUE = 0
CHECK_LIMIT_MAX = 1
CHECK_LIMIT = CHECK_LIMIT_MAX

LIMIT_VALUE = 0
LIMIT_MAX = 20

LOG_DIR = 'c:/microtrol/log/'
MASK = 'mgcsip'
SERVICE = 'mgcsip'
TIME_SLEEP = 60

ERR = 0
WARN = 1
INFO = 2
DBG = 3

TRACE_LEVEL = INFO

def trace(traceEntry, level):
    if level <= TRACE_LEVEL:
        print str(datetime.datetime.now()).split('.')[0] + ' ' + traceEntry

def getModDate(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def getLastFilename():
    fileDict = {}
    for dirname, dirnames, filenames in os.walk(LOG_DIR):
        for filename in filenames:
            if filename.lower().find(MASK) == -1:
                continue

            fileNameFull = os.path.join(dirname, filename).lower()
            modDate = getModDate(fileNameFull)
            fileDict[fileNameFull] = modDate

    fileListOrdered = sorted(fileDict.iteritems(), key=operator.itemgetter(1))

    lastFileName = fileListOrdered[-1][0]
    
    return lastFileName

timeLast = time.time()
#timeLast = time.time() - 120
fnameLast = ''
lineLast = -1

while True:

    fname = getLastFilename()
    trace('Last log file: ' + fname, DBG)

    f = open(fname, 'r')
    fbuff = f.readlines()
    f.close()

    i = 0 
    countValue = 0
    for l in fbuff:
        i +=1
        if fname == fnameLast and i < lineLast and lineLast != -1:
            continue
   
        try:
            t1 = l[0:17]
            t1 = time.mktime(time.strptime(t1, '%m/%d/%y %H:%M:%S'))
        except:
            continue

        if t1 < timeLast:
            continue
        
        if l.find(CHECK_LINE) != -1:
            countValue += 1

    fnameLast = fname
    lineLast = i

    trace('Count Value: ' + str(countValue), INFO)

    error = False
    if CHECK_LIMIT == CHECK_LIMIT_VALUE:
        if countValue == LIMIT_VALUE:
            error = True
    elif CHECK_LIMIT == CHECK_LIMIT_MAX:
        if countValue >= LIMIT_MAX:
            error = True

    if error:
        trace('Line: ' + CHECK_LINE + ' Count value: ' + str(countValue), ERR)
        os.system('c:\microtrol\trapgen\trapgen_custom.bat pykiller')
        if KILL:
            os.system('pskill ' + SERVICE)

    timeLast = time.time()
    time.sleep(TIME_SLEEP)