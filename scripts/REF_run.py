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

    self.DVFS = 1
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
    ######## Get start freq to calculate corrected Cycle ##############
    self.start_freq = []
    for core in range(sim.config.ncores):
        self.start_freq.append(sim.dvfs.get_frequency(core))


    ## makedir for stats coming out off energystats
    if not os.path.exists("%sstats"%sim.config.output_dir):
    	os.makedirs("%sstats"%sim.config.output_dir, 0777)
    ## mkdir for outfiles (files should be transfered between sniper and kalman)
    if not os.path.exists("%soutfiles"%sniper_path):
    	os.makedirs("%soutfiles"%sniper_path, 0777)

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
    self.filename_IPC="IPC.xls"
    self.Wfile_IPC = file(os.path.join(sim.config.output_dir, self.filename_IPC), 'w')
    self.Wfile_IPC.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_IPC.write("\t%d"%core)
    #############################
    self.filename_CPI="CPI.xls"
    self.Wfile_CPI = file(os.path.join(sim.config.output_dir, self.filename_CPI), 'w')
    self.Wfile_CPI.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_CPI.write("\t%d"%core)
    #############################
    self.filename_stall_time="stall_time.xls"
    self.Wfile_stall_time = file(os.path.join(sim.config.output_dir, self.filename_stall_time), 'w')
    self.Wfile_stall_time.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_stall_time.write("\t%d"%core)
    #############################
    self.filename_cpu_busy_time="cpu_busy_time.xls"
    self.Wfile_cpu_busy_time = file(os.path.join(sim.config.output_dir, self.filename_cpu_busy_time), 'w')
    self.Wfile_cpu_busy_time.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_cpu_busy_time.write("\t%d"%core)
    #############################
    self.filename_L3_uncore_time="L3_uncore_time.xls"
    self.Wfile_L3_uncore_time = file(os.path.join(sim.config.output_dir, self.filename_L3_uncore_time), 'w')
    self.Wfile_L3_uncore_time.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_L3_uncore_time.write("\t%d"%core)
    #############################
    self.filename_timing_summary="timing_summary.xls"
    self.Wfile_timing_summary = file(os.path.join(sim.config.output_dir, self.filename_timing_summary), 'w')
    self.Wfile_timing_summary.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_timing_summary.write("\t%d\tInstructions\tIPC\tTotalTime\tBusy\tCpuBusy\tStall\tl3Uncore\tFutex\tBaseTotal\tStallTotal"%core)


    #############################
    self.IdleTimePerc = []#number of cores = 1000 (I used alot)
    for core in range(sim.config.ncores):
        self.IdleTimePerc.append(0.0)
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
      snapshot_all = sniper_lib.get_results(resultsdir = sim.config.output_dir , partial = ('periodic-%d' % (0 *self.interval), 'periodic-%d' % ((self.num_snapshots) *self.interval ) ))['results']
      CoreIns = snapshot_last['core.instructions']
      IdleTime= snapshot_last['performance_model.idle_elapsed_time']
      BusyTime= snapshot_last['performance_model.nonidle_elapsed_time']
      CycleCount= snapshot_last['performance_model.cycle_count']
      TotalTime= snapshot_last['performance_model.elapsed_time']
      Futex= snapshot_last['performance_model.cpiSyncFutex']
      L3_uncore_total_time= snapshot_last['L3.uncore-totaltime']
      nonidle_elapsed_total_time= snapshot_last['performance_model.nonidle_elapsed_time']
      cpu_base_time= snapshot_last['interval_timer.cpiBase']

      stall_list = ['cpiBranchPredictor','cpiDataCachecache-remote','cpiDataCachedram','cpiDataCachedram-cache','cpiDataCachedram-local',\
                    'cpiDataCachedram-remote','cpiDataCacheL1','cpiDataCacheL1_S','cpiDataCacheL1I',\
                    'cpiDataCacheL2','cpiDataCacheL2_S','cpiDataCacheL3','cpiDataCacheL3_S','cpiDataCachemiss',\
                    'cpiDataCachenuca-cache','cpiDataCachepredicate-false','cpiDataCacheprefetch-no-mapping','cpiDataCacheunknown',\
                    'cpiInstructionCachecache-remote','cpiInstructionCachedram','cpiInstructionCachedram-cache',\
                    'cpiInstructionCachedram-local','cpiInstructionCachedram-remote','cpiInstructionCacheL1','cpiInstructionCacheL1_S',\
                    'cpiInstructionCacheL1I','cpiInstructionCacheL2','cpiInstructionCacheL2_S','cpiInstructionCacheL3',\
                    'cpiInstructionCacheL3_S','cpiInstructionCachemiss','cpiInstructionCachenuca-cache',\
                    'cpiInstructionCachepredicate-false','cpiInstructionCacheprefetch-no-mapping',\
                    'cpiInstructionCacheunknown','cpiLongLatency','cpiSerialization']


      for core in range(sim.config.ncores):
          self.IdleTimePerc[core]=float(IdleTime[core])/float(TotalTime[core])


      IPC = [] 
      CPI = [] 
      stall = []
      stall_cpi = []
      stall_time = [] #contains percentage of stall time/total time of the period
      cpu_busy_time = []
      futex_time = []
      stall_total_time = [] #contains counter time for for all the run
      L3_uncore_time = []      
      nonidle_elapsed_time= []

      for core in range(sim.config.ncores):
          stall.append(0)
          stall_cpi.append(0.0)
          stall_time.append(0.0)
          IPC.append(0.0)
          CPI.append(0.0) 
          cpu_busy_time.append(0.0)
          futex_time.append(0.0) 
          stall_total_time.append(0)        
          L3_uncore_time.append(0)
          nonidle_elapsed_time.append(0.0)

      for name in stall_list:
          stall_temp= snapshot_last['interval_timer.%s'%name]
          stall_temp_all= snapshot_all['interval_timer.%s'%name]
          for core in range(sim.config.ncores):
              stall[core]+=stall_temp[core] 
              stall_total_time[core]+=stall_temp_all[core]


      for core in range(sim.config.ncores):
          #stall_cpi[core] =  float(stall[core]) / (CoreIns[core]*sim.dvfs.get_frequency(core) ) 
          stall_time[core] = float(stall[core]) / TotalTime[core]
          cpu_busy_time[core] = 1-(self.IdleTimePerc[core]+stall_time[core])
          #cpu_busy_time[core]= cpu_base_time[core]
          futex_time[core] = float(Futex[core])/TotalTime[core]  
          L3_uncore_time[core] =  float(L3_uncore_total_time[core])/TotalTime[core]         
          nonidle_elapsed_time[core] =  float(nonidle_elapsed_total_time[core])/TotalTime[core]      

          print 'stall[%s]=%s\n'%(core,stall[core])
          # print 'cpi_stall[%s]=%s\n'%(core,stall_cpi[core])
          print 'time_stall[%s]=%s\n'%(core,stall_time[core]) 
          print 'idletimePerc[%s]=%s\n'%(core,self.IdleTimePerc[core])
          print 'non-stall-busy-time[%s]=%s\n'%(core,1-(self.IdleTimePerc[core]+stall_time[core]))  

   
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
      #for core in range(sim.config.ncores):
      #   print ((sim.dvfs.get_frequency(core)/1000.0)*(self.interval/1000000))
      #raw_input()

      ############## IPC ##############################################################
      self.Wfile_IPC = file(os.path.join(sim.config.output_dir, self.filename_IPC), 'a')
      self.Wfile_IPC.write('\n')
      self.Wfile_IPC.write('%d\t'%(self.num_snapshots))
      self.Wfile_IPC.write('IPC')
      for core in range(sim.config.ncores):
          self.Wfile_IPC.write("\t%f"%(int(CoreIns[core])/((sim.dvfs.get_frequency(core)/1000.0)*(self.interval/1000000))))
          IPC[core] = (int(CoreIns[core])/((sim.dvfs.get_frequency(core)/1000.0)*(self.interval/1000000)))
      self.Wfile_IPC.close()

      ############## CPI ##############################################################
      self.Wfile_CPI = file(os.path.join(sim.config.output_dir, self.filename_CPI), 'a')
      self.Wfile_CPI.write('\n')
      self.Wfile_CPI.write('%d\t'%(self.num_snapshots))
      self.Wfile_CPI.write('CPI')
      for core in range(sim.config.ncores):
          if (CoreIns[core]==0):
		       self.Wfile_CPI.write ("\t0")
		       CPI[core]=0.0
          else:
		       #self.Wfile_CPI.write("\t%f"%(float(cpu_base_time[core])/CoreIns[core]))
		       #CPI[core]=  float(cpu_base_time[core])/CoreIns[core]             

		       self.Wfile_CPI.write("\t%f"%(1.0/IPC[core]))
		       CPI[core]= 1.0/IPC[core]            
 
#         if ((int(CoreIns[core])/((sim.dvfs.get_frequency(core)/1000.0)*(self.interval/1000000))) == 0):
#		       self.Wfile_CPI.write ("\tinf")
#          else: self.Wfile_CPI.write("\t%f"%(1/(int(CoreIns[core])/((sim.dvfs.get_frequency(core)/1000.0)*(self.interval/1000000)))))


      self.Wfile_CPI.close()
      
      ############## stall_time ##############################################################
      self.Wfile_stall_time = file(os.path.join(sim.config.output_dir, self.filename_stall_time), 'a')
      self.Wfile_stall_time.write('\n')
      self.Wfile_stall_time.write('%d\t'%(self.num_snapshots))
      self.Wfile_stall_time.write('stall_time')
      for core in range(sim.config.ncores):
          self.Wfile_stall_time.write("\t%s"%stall_time[core])
      self.Wfile_stall_time.close()
      
      ############## cpu_busy_time ############################################################## just the (busy_time - stalls)
      self.Wfile_cpu_busy_time = file(os.path.join(sim.config.output_dir, self.filename_cpu_busy_time), 'a')
      self.Wfile_cpu_busy_time.write('\n')
      self.Wfile_cpu_busy_time.write('%d\t'%(self.num_snapshots))
      self.Wfile_cpu_busy_time.write('cpu_busy_time')
      for core in range(sim.config.ncores):
          self.Wfile_cpu_busy_time.write("\t%s"%cpu_busy_time[core])
      self.Wfile_cpu_busy_time.close()

      ##############L3_uncore_time##############################################################
      self.Wfile_L3_uncore_time = file(os.path.join(sim.config.output_dir, self.filename_L3_uncore_time), 'a')
      self.Wfile_L3_uncore_time.write('\n')
      self.Wfile_L3_uncore_time.write('%d\t'%(self.num_snapshots))
      self.Wfile_L3_uncore_time.write('L3_uncore_time')
      for core in range(sim.config.ncores):
          self.Wfile_L3_uncore_time.write("\t%s"%L3_uncore_time[core])
      self.Wfile_L3_uncore_time.close()


      ############## timing_summary ############################################################## just the (busy_time - stalls)
      self.Wfile_timing_summary = file(os.path.join(sim.config.output_dir, self.filename_timing_summary), 'a')
      self.Wfile_timing_summary.write('\n')
      self.Wfile_timing_summary.write('%d\t'%(self.num_snapshots))
      self.Wfile_timing_summary.write('timing_summary')
      for core in range(sim.config.ncores):
          self.Wfile_timing_summary.write("\t----\t%s\t%s\t1\t%s\t%s\t%s\t%s\t%s\t%s\t%s"%(CoreIns[core],IPC[core],(1-self.IdleTimePerc[core]),cpu_busy_time[core],stall_time[core],L3_uncore_time[core],futex_time[core],cpu_base_time[core],stall_total_time[core]))
      self.Wfile_timing_summary.close()

      
      ################################ CacheMiss ########################################    
      #periodic stat in stats file,
      #it also generates cachemiss files in the output
      gen_simout.generate_simout(resultsdir = sim.config.output_dir, partial = ('periodic-%d' % ((self.num_snapshots-1) *self.interval), 'periodic-%d' % ((self.num_snapshots) *self.interval ) ), output = open(os.path.join(sim.config.output_dir, 'stats/p%d.out'%self.num_snapshots), 'w'), silent = True)
      ########################################################################################

      print '\nperiodic-%d - periodic-%d\n' %( (self.num_snapshots *self.interval), ((self.num_snapshots-1)))

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
      self.fd.write('periodic-%d' % (self.num_snapshots * self.interval))      
      self.next_interval += self.interval



sim.util.register(PeriodicStats())
