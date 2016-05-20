from os import listdir
from os.path import isfile, join


def check(mypath="./", jobname="M750"):    
    failed = []
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and "job_"+jobname in f and ".o" in f]
    count = len(onlyfiles)
    print "Checking ", jobname, "with", count, "files"
    for f in onlyfiles:
        fo = open(join(mypath,f),'r')
        is_success = False
        for line in fo:
            if "Done!" in line or "Return because no files could be opened" in line:
                #print "\tJob ", f, " finished properly"
                is_success = True
                count -= 1
                break
        if not is_success:
            failed.append(f)
        fo.close()
    print "\t%.0f jobs have failed:" % count, failed

###############################

#check("../test/", "M750")
check("../test/", "HT100to200")
check("../test/", "HT200to300")
check("../test/", "HT300to500")
check("../test/", "HT500to700")
check("../test/", "HT700to1000")
check("../test/", "HT1500to2000")
check("../test/", "HT2000toInf")
check("../test/", "Run2015C")
check("../test/", "Run2015D")
check("../test/", "Spin0_M650")
check("../test/", "Spin0_M750")
check("../test/", "Spin0_M850")
check("../test/", "Spin0_M1000")
check("../test/", "Spin0_M1200")
check("../test/", "Spin2_M650")
check("../test/", "Spin2_M750")
check("../test/", "Spin2_M850")
check("../test/", "Spin2_M1000")
check("../test/", "Spin2_M1200")
check("../test/", "TT_ext3")
check("../test/", "ST_t_atop")
check("../test/", "ST_t_top")
check("../test/", "ST_tW_atop")
check("../test/", "ST_tW_top")

