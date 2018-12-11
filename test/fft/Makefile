TARGET=fft
include ../shared/Makefile.shared

$(TARGET): $(TARGET).o
	$(CC) $(TARGET).o -lm $(SNIPER_LDFLAGS) -o $(TARGET)

run_$(TARGET):
#	../../run-sniper -n 6 -c gainestown --roi --viz -s ../../scripts/ipctrace.py::10000 -- ./fft -p 4
#	../../run-sniper -n 6 -c gainestown --roi --viz -s ../../scripts/ipcthreadtrace.py::10000 -- ./fft -p 4
#	../../run-sniper -n 6 -c gainestown --roi --viz -s scheduler-locality -- ./fft -p 16
#	../../run-sniper -n 6 -c gainestown --roi -d ./outfile --viz -s stattrace:core.bbv-0::10 -- ./fft -p 16 
#	../../run-sniper -n 2 -c gainestown --roi -d ./out1core -s periodic-stats:10000:0 -- ./fft -p 8
#	../../run-sniper -n 4 -c gainestown -c noc --roi -d ./outfile -s energystats:100 -- ./fft -p 4
#	../../run-sniper -n 4 -c gainestown --roi -d ./outfile -s myDVFS::10000 -- ./fft -p 4
#	../../run-sniper -n 4 -c gainestown --roi -d ./outfile -s periodic-stats:10000:0 -- ./fft -p 4
#	../../run-sniper -n 4 -c gainestown --roi -d ./outfile_DVFS -speriodic-stats:10000:0 -senergystats.py -sstattrace:core.energy-dynamic -- ./fft -p 4
#	../../run-sniper -n 4 -c gainestown --roi -d ./outfile -s periodic-stats:10000:0 -s energystats.py -- ./fft -p 4

#	../../run-sniper -n 4 -c gainestown --roi -d ./outfile_DVFS -speriodic-stats:10000:0 -senergystats.py -sstattrace:core.energy-dynamic -sstattrace:core.energy-static -sstattrace:processor.energy-static -- ./fft -p 4

	../../run-sniper -n 16 -c gainestown -c noc --roi -d ./test_16c_test02-2 -speriodic-stats:10000:0 -senergystats:10000  -g --perf_model/core/frequency=2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2 -- ./fft -p 16

#	../../run-sniper -n 2 -c gainestown -c noc --roi -d ./test_2th_futex -speriodic-stats:10000:0 -senergystats:10000  -g --perf_model/core/frequency=2,2 -- ./fft -p 2


CLEAN_EXTRA=viz
#../../tools/dumpstats.py --partial periodic-5000000000:periodic-11100000000 | grep core.instructions
