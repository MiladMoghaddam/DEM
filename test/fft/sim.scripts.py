import sys
sys.argv = [ "/home/milad/sniper/scripts/periodic-stats.py", "1000:2000" ]
execfile("/home/milad/sniper/scripts/periodic-stats.py")
sys.argv = [ "/home/milad/sniper/scripts/markers.py", "markers" ]
execfile("/home/milad/sniper/scripts/markers.py")
