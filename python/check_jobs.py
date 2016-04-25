from os import listdir
from os.path import isfile, join


def check(mypath="./", jobname="M750"):    
    failed = []
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and "job_"+jobname in f and ".o" in f]
    count = len(onlyfiles)
    for f in onlyfiles:
        fo = open(f,'r')
        is_success = False
        for line in fo:
            if "Done!" in line or "Return because no files could be opened" in line:
                #print "\tJob ", f, " finished properly"
                is_success = True
                count -= 1
                break
        if not is_success:
            failed.append(f)
    print "%.0f jobs have failed:" % count, failed

###############################

check("./", "HT700to1000")
