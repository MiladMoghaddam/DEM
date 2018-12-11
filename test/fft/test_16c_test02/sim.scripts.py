import sys
sys.argv = [ "/home/milad/sniper/scripts/periodic-stats.py", "10000:0" ]
execfile("/home/milad/sniper/scripts/periodic-stats.py")
sys.argv = [ "/home/milad/sniper/scripts/energystats.py", "10000" ]
execfile("/home/milad/sniper/scripts/energystats.py")
