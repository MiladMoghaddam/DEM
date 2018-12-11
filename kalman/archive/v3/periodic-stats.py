"""
periodic-stats.py

Periodically write out all statistics
1st argument is the interval size in nanoseconds (default is 1e9 = 1 second of simulated time)
2rd argument, if present will limit the number of snapshots and dynamically remove itermediate data
"""

import sim, os, sys
sys.path.insert(0, '/home/milad/sniper/tools/')
import sniper_lib
import gen_simout

#############################################
sniper_path= "/home/milad/sniper/"
#############################################
class PeriodicStats:
  def setup(self, args):
    args = dict(enumerate((args or '').split(':')))
    interval = long(args.get(0, '') or 1000000000)

    self.DVFS = 0
    self.max_snapshots = long(args.get(1, 0))
    self.num_snapshots = 0
    self.interval = long(interval * sim.util.Time.NS)
    self.next_interval = float('inf')
    self.in_roi = False
    #sim.util.Every(self.interval, self.periodic, roi_only = True)
    self.sd = sim.util.StatsDelta()

    self.stats = {
      'time': [ self.sd.getter('performance_model', core, 'elapsed_time') for core in range(sim.config.ncores) ],
      'ffwd_time': [ self.sd.getter('fastforward_performance_model', core, 'fastforwarded_time') for core in range(sim.config.ncores) ],
      'instrs': [ self.sd.getter('performance_model', core, 'instruction_count') for core in range(sim.config.ncores) ],
      'coreinstrs': [ self.sd.getter('core', core, 'instructions') for core in range(sim.config.ncores) ],
    }
    
    sim.util.Every(self.interval, self.periodic, statsdelta = self.sd, roi_only = True)#interval_ns * sim.util.Time.NS
    #############################
    ## makedir for stats coming out off energystats
    if not os.path.exists("%sstats"%sim.config.output_dir):
    	os.makedirs("%sstats"%sim.config.output_dir, 0777)
    ## mkdir for outfiles (files should be transfered between sniper and kalman)
    if not os.path.exists("%soutfiles"%sniper_path):
    	os.makedirs("%soutfiles"%sniper_path, 0777)

    #############################
    self.filename_kalmanOut = "kalmanOut.xls"
	#############################
    filename="statsPeriodic.txt"
    self.fd = file(os.path.join(sim.config.output_dir, filename), 'w')
    #############################
    self.filename_CoreIns="CoreIns.xls"
    self.Wfile_CoreIns = file(os.path.join(sim.config.output_dir, self.filename_CoreIns), 'w')
    self.Wfile_CoreIns.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_CoreIns.write("\t%d"%core)
    #############################
    self.filename_IdleTime="IdleTime.xls"
    self.Wfile_IdleTime = file(os.path.join(sim.config.output_dir, self.filename_IdleTime), 'w')
    self.Wfile_IdleTime.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_IdleTime.write("\t%d"%core)
    #############################
    self.filename_IdleTimePerc="IdleTimePerc.xls"
    self.Wfile_IdleTimePerc = file(os.path.join(sim.config.output_dir, self.filename_IdleTimePerc), 'w')
    self.Wfile_IdleTimePerc.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_IdleTimePerc.write("\t%d"%core)

    #############################
    self.IdleTimePerc = []#number of cores = 1000 (I used alot)
    for core in range(sim.config.ncores):
        self.IdleTimePerc.append(0.0)
    #############################
    self.predicted_CoreIns = []
    for core in range(sim.config.ncores):
        self.predicted_CoreIns.append([])
    #############################


  def hook_roi_begin(self):
    self.in_roi = True
    self.next_interval = sim.stats.time() + self.interval
    sim.stats.write('periodic-0')
    self.fd.write('periodic-0')

  def hook_roi_end(self):
    self.next_interval = float('inf')
    self.in_roi = False

  def periodic(self, time, time_delta):
    if self.max_snapshots and self.num_snapshots > self.max_snapshots:
      self.num_snapshots /= 2
      for t in range(self.interval, time, self.interval * 2):
        sim.util.db_delete('periodic-%d' % t)
      self.interval *= 2

    if time >= self.next_interval:
      self.num_snapshots += 1
      sim.stats.write('periodic-%d' % (self.num_snapshots * self.interval))
      #################################################
      ######### snapshot_last #########################
      snapshot_last = sniper_lib.get_results(resultsdir = sim.config.output_dir , partial = ('periodic-%d' % ((self.num_snapshots-1) *self.interval), 'periodic-%d' % ((self.num_snapshots) *self.interval ) ))['results']
      CoreIns = snapshot_last['core.instructions']
      IdleTime= snapshot_last['performance_model.idle_elapsed_time']
      BusyTime= snapshot_last['performance_model.nonidle_elapsed_time']
      CycleCount= snapshot_last['performance_model.cycle_count']
      TotalTime= snapshot_last['performance_model.elapsed_time']
     
      for core in range(sim.config.ncores):
          self.IdleTimePerc[core]=float(IdleTime[core])/float(TotalTime[core])


      IdleTimePercentage= IdleTime[0]/TotalTime[0]
      BusyTimePercentage= BusyTime[0]/TotalTime[0]	#just for the first core

      ##############CoreIns##############################################################
      self.Wfile_CoreIns = file(os.path.join(sim.config.output_dir, self.filename_CoreIns), 'a')
      self.Wfile_CoreIns.write('\n')
      self.Wfile_CoreIns.write('%d\t'%(self.num_snapshots))
      self.Wfile_CoreIns.write('CoreIns')
      for core in range(sim.config.ncores):
          self.Wfile_CoreIns.write("\t%s"%CoreIns[core])
      self.Wfile_CoreIns.close()

      ##############IdleTime##############################################################
      self.Wfile_IdleTime = file(os.path.join(sim.config.output_dir, self.filename_IdleTime), 'a')
      self.Wfile_IdleTime.write('\n')
      self.Wfile_IdleTime.write('%d\t'%(self.num_snapshots))
      self.Wfile_IdleTime.write('IdleTime')
      for core in range(sim.config.ncores):
          self.Wfile_IdleTime.write("\t%s"%IdleTime[core])
      self.Wfile_IdleTime.close()
      
      ##############IdleTimePerc##############################################################
      self.Wfile_IdleTimePerc = file(os.path.join(sim.config.output_dir, self.filename_IdleTimePerc), 'a')
      self.Wfile_IdleTimePerc.write('\n')
      self.Wfile_IdleTimePerc.write('%d\t'%(self.num_snapshots))
      self.Wfile_IdleTimePerc.write('IdleTimePerc')
      for core in range(sim.config.ncores):
          self.Wfile_IdleTimePerc.write("\t%f"%self.IdleTimePerc[core])
      self.Wfile_IdleTimePerc.close()
      ########################################################################################      

      print '\nperiodic-%d - periodic-%d\n' %( (self.num_snapshots *self.interval), ((self.num_snapshots-1)))
      print 'CoreIns= %s'%CoreIns
      print 'IdleTime= %s'%IdleTime
      print 'BusyTime= %s'%BusyTime
      print 'CycleCount= %s'%CycleCount
      print 'TotalTime= %s'%TotalTime

      ##############################################################
      ################# Kalman #####################################
      #self.predicted_CoreIns[core][self.num_snapshots-1]

      os.system ("%skalman/build/kalman-test %s %s"%(sniper_path, os.path.join(sim.config.output_dir, self.filename_CoreIns), os.path.join(sim.config.output_dir, self.filename_kalmanOut)))

      ##############################################################
      ############### Get Kalman predicted results ################
      self.Rfile_kalmanOut = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut), 'r')
      total_line_count=-1
      for line in self.Rfile_kalmanOut:
		  total_line_count+=1  

      self.Rfile_kalmanOut = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut), 'r')
      line_count=-1
      for line in self.Rfile_kalmanOut:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count>=2) and (line_count == total_line_count): #stats_lines (we dont read last line, it just has the predicted value not the future one)
              for core in range(sim.config.ncores):
				  self.predicted_CoreIns[core].append(float(line_splitted[5*core+3]))  #offset=4  in the file 
      

      ##############################################################
      ################# DVFS #######################################
      if self.DVFS:
          self.fd.write('%u' % (time / 1e6)) # Time in ns
          for core in range(sim.config.ncores):
              # detailed-only IPC    
              self.fd.write(' f: %.2fGHz' %(sim.dvfs.get_frequency(core)/1000.0))
              #raw_input()
              #if (self.IdleTimePerc[core]>0.4):
              #if (core==0):              
              if (self.num_snapshots%2==0):
              #if (self.predicted_CoreIns[core][self.num_snapshots-1] < 2000.0) :                  
                  sim.dvfs.set_frequency(core,3000)
              else: 
                  sim.dvfs.set_frequency(core,1500)
                  
              print "predicted: "
              print self.predicted_CoreIns[core][self.num_snapshots-1]

              cycles = (self.stats['time'][core].delta - self.stats['ffwd_time'][core].delta) * sim.dvfs.get_frequency(core) / 1e9 # convert fs to cycles
              instrs = self.stats['instrs'][core].delta
              ipc = instrs / (cycles or 1) # Avoid division by zero
              #self.fd.write(' %.3f' % ipc)

              # include fast-forward IPCs
              cycles = self.stats['time'][core].delta * sim.dvfs.get_frequency(core) / 1e9 # convert fs to cycles
              instrs = self.stats['coreinstrs'][core].delta
              ipc = instrs / (cycles or 1)
              self.fd.write(' %.3f' % ipc)
          self.fd.write('\n')

      ############################################################## 
      #os.system("/home/milad/sniper/tools/dumpstats.py --partial periodic-%d:periodic-%d | grep power.Core"%( ((self.num_snapshots-1) *self.interval), ((self.num_snapshots) *self.interval ) ) )

      #raw_input(); #getch
      self.fd.write('periodic-%d' % (self.num_snapshots * self.interval))      


      gen_simout.generate_simout(resultsdir = sim.config.output_dir, partial = ('periodic-%d' % ((self.num_snapshots-1) *self.interval), 'periodic-%d' % ((self.num_snapshots) *self.interval ) ), output = open(os.path.join(sim.config.output_dir, 'stats/p%d.out'%self.num_snapshots), 'w'), silent = True)
      #gen_simout.generate_simout(resultsdir = sim.config.output_dir, partial = ('periodic-10000000000','periodic-20000000000'), output = open(os.path.join(sim.config.output_dir, 'stats/p%d.out'%self.num_snapshots), 'w'), silent = True)

      self.next_interval += self.interval



sim.util.register(PeriodicStats())
