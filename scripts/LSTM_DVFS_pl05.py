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

#from LSTM import LSTM_predict

#############################################
sniper_path= "/home/milad/sniper/"
#############################################
freq_H = 2000.0

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

    ############# Kalman ############
    self.filename_kalmanOut_CoreIns = "kalmanOut_CoreIns.xls"
    self.filename_kalmanOut_IdleTimePerc = "kalmanOut_IdleTimePerc.xls"
    self.filename_kalmanOut_Workload = "kalmanOut_Workload.xls"
    self.filename_kalmanOut_IPC = "kalmanOut_IPC.xls"
    self.filename_kalmanOut_cpu_busy_time = "kalmanOut_cpu_busy_time.xls"
    self.filename_kalmanOut_stall_time = "kalmanOut_stall_time.xls"
    self.filename_kalmanOut_CPI = "kalmanOut_CPI.xls"
    self.filename_Workload = "Workload.xls" #This file is generated in energystats.py
    self.filename_kalmanOut_L3_uncore_time = "kalmanOut_L3_uncore_time.xls"
	#############################
    filename="statsPeriodic.txt"
    self.fd = file(os.path.join(sim.config.output_dir, filename), 'w')

    #############################
    self.filename_SummaryDVFS="SummaryDVFS.xls"
    self.Wfile_SummaryDVFS = file(os.path.join(sim.config.output_dir, self.filename_SummaryDVFS), 'w')
    self.Wfile_SummaryDVFS.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_SummaryDVFS.write("\t\t%d\tPredFrequency\tCorrectedFrequency\tInsDone\tPredictedInsDone\tIns_ref\tPredcited_ref\tActualLoss\tPredictedLoss\tActualLossRate\tPredictedLossRate\tTotalActualInst\tTotalPredictedIns\tTotalActualMissRate\tTotalPredictedMissRate\tPF_time\tPF_pred_time\t"%core)

    #############################
    self.filename_Frequencies="Frequencies.xls"
    self.Wfile_Frequencies = file(os.path.join(sim.config.output_dir, self.filename_Frequencies), 'w')
    self.Wfile_Frequencies.write("%d\t"%(sim.config.ncores))
    for core in range(sim.config.ncores):
        self.Wfile_Frequencies.write("%d-pred\t%d-corrected\t"%(core,core))

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
    self.filename_LSTM_cpu_busy_time="LSTM_cpu_busy_time.xls"
    self.Wfile_LSTM_cpu_busy_time = file(os.path.join(sim.config.output_dir, self.filename_LSTM_cpu_busy_time), 'w')
    self.Wfile_LSTM_cpu_busy_time.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_LSTM_cpu_busy_time.write("\t%d"%core)
    self.Wfile_LSTM_cpu_busy_time.write("\n") #one line delay
    self.Wfile_LSTM_cpu_busy_time.close()
    #############################
    self.filename_LSTM_IdleTimePerc="LSTM_IdleTimePerc.xls"
    self.Wfile_LSTM_IdleTimePerc = file(os.path.join(sim.config.output_dir, self.filename_LSTM_IdleTimePerc), 'w')
    self.Wfile_LSTM_IdleTimePerc.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_LSTM_IdleTimePerc.write("\t%d"%core)
    self.Wfile_LSTM_IdleTimePerc.write("\n") #one line delay
    self.Wfile_LSTM_IdleTimePerc.close()
    #############################
    self.filename_LSTM_CoreIns="LSTM_CoreIns.xls"
    self.Wfile_LSTM_CoreIns = file(os.path.join(sim.config.output_dir, self.filename_LSTM_CoreIns), 'w')
    self.Wfile_LSTM_CoreIns.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_LSTM_CoreIns.write("\t%d"%core)
    self.Wfile_LSTM_CoreIns.write("\n") #one line delay
    self.Wfile_LSTM_CoreIns.close()

    #############################
    self.filename_LSTM_IPC="LSTM_IPC.xls"
    self.Wfile_LSTM_IPC = file(os.path.join(sim.config.output_dir, self.filename_LSTM_IPC), 'w')
    self.Wfile_LSTM_IPC.write("%d\tcore"%sim.config.ncores)
    for core in range(sim.config.ncores):
        self.Wfile_LSTM_IPC.write("\t%d"%core)
    self.Wfile_LSTM_IPC.write("\n") #one line delay
    self.Wfile_LSTM_IPC.close()

    #############################
    self.IdleTimePerc = []#number of cores = 1000 (I used alot)
    for core in range(sim.config.ncores):
        self.IdleTimePerc.append(0.0)
    ########## Kalman predictions #########
    self.predicted_CoreIns = []
    self.predicted_IdleTimePerc = []  
    self.predicted_Workload = []
    self.predicted_IPC = []
    self.predicted_cpu_busy_time = [] # busy_time - stalls
    self.predicted_stall_time = []
    self.predicted_CPI = []
    self.predicted_L3_uncore_time = []
    for core in range(sim.config.ncores):
        self.predicted_CoreIns.append([])
        self.predicted_IdleTimePerc.append([])
        self.predicted_Workload.append([])
        self.predicted_IPC.append([])
        self.predicted_cpu_busy_time.append([])
        self.predicted_stall_time.append([])
        self.predicted_CPI.append([])
        self.predicted_L3_uncore_time.append([])

    ###### DVFS method parameters #############    
    self.TotalInstDone = []
    self.TotallInstLoss = []
    self.TotallInstDone = []           
    self.TotalInstLossRate = []
    self.PredictedInstLoss = []
    self.PredictedInstDone = [] 
    self.PredictedInstLossRate = []
    self.PredictedTotalInstLoss = []
    self.PredictedTotalInstDone = [] 
    self.PredictedTotalInstLossRate = []
    self.InstLoss = [] 
    self.InstDone = [] 
    self.InstLossRate = []
    self.T_delay = []
    self.T_ref_corrected = []
    self.T_delay_corrected = []
    self.T_ref = []
    self.T_delay_next = []
    self.T_ref_next = []
    self.T_delay_prev_corrected = []
    self.T_ref_prev_corrected = []
    self.PF = []
    self.PF_next = []
    self.PF_prev_corrected = []
    self.PredictedInst_for_freq_H = []
    self.PredictedTotalInst_for_freq_H = []
    self.Inst_for_freq_H = []
    self.TotalInst_for_freq_H = []
    self.freq_corrected = []
    self.sum_inst = []
    for core in range(sim.config.ncores):    
        self.TotalInstDone.append(0)
        self.TotallInstLoss.append(0)
        self.TotallInstDone.append(0)       
        self.TotalInstLossRate.append(0.0)
        self.PredictedInstLoss.append(0)
        self.PredictedInstDone.append(0) 
        self.PredictedInstLossRate.append(0.0)
        self.PredictedTotalInstLoss.append(0) 
        self.PredictedTotalInstDone.append(0) 
        self.PredictedTotalInstLossRate.append(0.0)
        self.InstLoss.append(0) 
        self.InstDone.append(0) 
        self.InstLossRate.append(0.0)
        self.T_delay.append(0.0)
        self.T_ref.append(0.0)
        self.T_delay_next.append(0.0)
        self.T_ref_next.append(0.0)
        self.PF.append(0.0)
        self.PF_next.append(0.0)
        self.PredictedInst_for_freq_H.append(0.0)
        self.PredictedTotalInst_for_freq_H.append(0.0)
        self.Inst_for_freq_H.append(0.0)
        self.TotalInst_for_freq_H.append(0.0)
        self.T_ref_corrected.append(0.0)
        self.T_delay_corrected.append(0.0)
        self.T_delay_prev_corrected.append(0.0)
        self.T_ref_prev_corrected.append(0.0)
        self.PF_prev_corrected.append(0.0)
        self.freq_corrected.append(int(freq_H))
        self.sum_inst.append(0.0)

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
          try:
              self.Wfile_IPC.write("\t%f"%(int(CoreIns[core])/((sim.dvfs.get_frequency(core)/1000.0)*(1-self.IdleTimePerc[core])*(self.interval/1000000))))#
              IPC[core] = (int(CoreIns[core])/((sim.dvfs.get_frequency(core)/1000.0)*(1-self.IdleTimePerc[core])*(self.interval/1000000)))#
          except:
              self.Wfile_IPC.write("\t0.0000001") # almost 0             
              IPC[core] = 0.0000001

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
      print 'CoreIns= %s'%CoreIns
      print 'IdleTime= %s'%IdleTime
      print 'BusyTime= %s'%BusyTime
      print 'CycleCount= %s'%CycleCount
      print 'TotalTime= %s'%TotalTime

      ##############################################################
      ################# Kalman #####################################
      #self.predicted_CoreIns[core][self.num_snapshots-1]

      os.system ("%skalman/build/kalman-test %s %s"%(sniper_path, os.path.join(sim.config.output_dir, self.filename_CoreIns),\
                  os.path.join(sim.config.output_dir, self.filename_kalmanOut_CoreIns)))
      os.system ("%skalman/build/kalman-test %s %s"%(sniper_path, os.path.join(sim.config.output_dir, self.filename_CPI),\
                  os.path.join(sim.config.output_dir, self.filename_kalmanOut_CPI)))


      os.system ("%skalman/build/kalman-test %s %s"%(sniper_path, os.path.join(sim.config.output_dir, self.filename_IdleTimePerc),\
                  os.path.join(sim.config.output_dir, self.filename_kalmanOut_IdleTimePerc)))
      '''
      os.system ("%skalman/build/kalman-test %s %s"%(sniper_path, os.path.join(sim.config.output_dir, self.filename_IPC),\
                  os.path.join(sim.config.output_dir, self.filename_kalmanOut_IPC)))
      '''      
      os.system ("%skalman/build/kalman-test %s %s"%(sniper_path, os.path.join(sim.config.output_dir, self.filename_cpu_busy_time),\
                  os.path.join(sim.config.output_dir, self.filename_kalmanOut_cpu_busy_time)))
      '''
      os.system ("%skalman/build/kalman-test %s %s"%(sniper_path, os.path.join(sim.config.output_dir, self.filename_stall_time),\
                  os.path.join(sim.config.output_dir, self.filename_kalmanOut_stall_time)))

      os.system ("%skalman/build/kalman-test %s %s"%(sniper_path, os.path.join(sim.config.output_dir, self.filename_L3_uncore_time),\
                  os.path.join(sim.config.output_dir, self.filename_kalmanOut_L3_uncore_time)))
      '''
      ##################################################################################
      ##################################################################################
      input_file_path = os.path.join(sim.config.output_dir, self.filename_cpu_busy_time)
      output_file_path = os.path.join(sim.config.output_dir,'LSTM_pred_CPU_busy_time.txt')
      trained_model_name ='trained_cpu_busy_time'
      os.system ("python %sscripts/LSTM_predict.py %s %s %s %s"%(sniper_path,input_file_path,output_file_path,str(sim.config.ncores),trained_model_name))#window_size is set in LSTM_UL
      with open(output_file_path, 'r') as f:
           first_line = f.readline()
      LSTM_pred_CPU_busy_time=first_line.split(',')

      self.Wfile_LSTM_cpu_busy_time = file(os.path.join(sim.config.output_dir, self.filename_LSTM_cpu_busy_time), 'a')
      self.Wfile_LSTM_cpu_busy_time.write('\n\t')
      for core in range(sim.config.ncores):
        self.Wfile_LSTM_cpu_busy_time.write("\t%s"%float(LSTM_pred_CPU_busy_time[core]))
      self.Wfile_LSTM_cpu_busy_time.close()

      ###################################################################################
      input_file_path = os.path.join(sim.config.output_dir, self.filename_IdleTimePerc)
      output_file_path = os.path.join(sim.config.output_dir,'LSTM_pred_IdleTimePerc.txt')
      trained_model_name = 'trained_IdleTimePerc'
      os.system ("python %sscripts/LSTM_predict.py %s %s %s %s"%(sniper_path,input_file_path,output_file_path,str(sim.config.ncores),trained_model_name))#window_size is set in LSTM_UL
      with open(output_file_path, 'r') as f:
           first_line = f.readline()
      LSTM_pred_IdleTimePerc=first_line.split(',')          

      self.Wfile_LSTM_IdleTimePerc = file(os.path.join(sim.config.output_dir, self.filename_LSTM_IdleTimePerc), 'a')
      self.Wfile_LSTM_IdleTimePerc.write('\n\t')
      for core in range(sim.config.ncores):
        self.Wfile_LSTM_IdleTimePerc.write("\t%s"%float(LSTM_pred_IdleTimePerc[core]))
      self.Wfile_LSTM_IdleTimePerc.close()

      ##################################################################################
      input_file_path = os.path.join(sim.config.output_dir, self.filename_CoreIns)
      output_file_path = os.path.join(sim.config.output_dir,'LSTM_pred_CoreIns.txt')
      trained_model_name ='trained_CoreIns'
      os.system ("python %sscripts/LSTM_predict.py %s %s %s %s"%(sniper_path,input_file_path,output_file_path,str(sim.config.ncores),trained_model_name))#window_size is set in LSTM_UL
      with open(output_file_path, 'r') as f:
           first_line = f.readline()
      LSTM_pred_CoreIns=first_line.split(',')

      self.Wfile_LSTM_CoreIns = file(os.path.join(sim.config.output_dir, self.filename_LSTM_CoreIns), 'a')
      self.Wfile_LSTM_CoreIns.write('\n\t')
      for core in range(sim.config.ncores):
        self.Wfile_LSTM_CoreIns.write("\t%s"%float(LSTM_pred_CoreIns[core]))
      self.Wfile_LSTM_CoreIns.close()

      ##################################################################################
      input_file_path = os.path.join(sim.config.output_dir, self.filename_IPC)
      output_file_path = os.path.join(sim.config.output_dir,'LSTM_pred_IPC.txt')
      trained_model_name ='trained_IPC'
      os.system ("python %sscripts/LSTM_predict.py %s %s %s %s"%(sniper_path,input_file_path,output_file_path,str(sim.config.ncores),trained_model_name))#window_size is set in LSTM_UL
      with open(output_file_path, 'r') as f:
           first_line = f.readline()
      LSTM_IPC=first_line.split(',')

      self.Wfile_LSTM_IPC = file(os.path.join(sim.config.output_dir, self.filename_LSTM_IPC), 'a')
      self.Wfile_LSTM_IPC.write('\n\t')
      for core in range(sim.config.ncores):
        self.Wfile_LSTM_IPC.write("\t%s"%float(LSTM_IPC[core]))
      self.Wfile_LSTM_IPC.close()

      ##############################################################
      ############### Get Kalman predicted results ################
      ######### kalmanOut_CoreIns
      
      self.Rfile_kalmanOut_CoreIns = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_CoreIns), 'r')
      total_line_count=-1
      for line in self.Rfile_kalmanOut_CoreIns:
		  total_line_count+=1  
      
      self.Rfile_kalmanOut_CoreIns = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_CoreIns), 'r')
      line_count=-1
      for line in self.Rfile_kalmanOut_CoreIns:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count>=2) and (line_count == total_line_count): 
              for core in range(sim.config.ncores):
				  self.predicted_CoreIns[core].append(float(line_splitted[5*core+3]))  #offset=3  in the file 
      
      '''
      #note: self.predicted_CoreIns[core][self.num_snapshots-1] shows the last prediction for core= ...
      '''
      ######## kalmanOut_IdleTimePerc   
      self.Rfile_kalmanOut_IdleTimePerc = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_IdleTimePerc), 'r')
      line_count=-1
      for line in self.Rfile_kalmanOut_IdleTimePerc:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count>=2) and (line_count == total_line_count): 
              for core in range(sim.config.ncores):
				  self.predicted_IdleTimePerc[core].append(float(line_splitted[5*core+3]))  #offset=3  in the file 
      '''
      ######## kalmanOut_IPC   
      self.Rfile_kalmanOut_IPC = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_IPC), 'r')
      line_count=-1
      for line in self.Rfile_kalmanOut_IPC:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count>=2) and (line_count == total_line_count): 
              for core in range(sim.config.ncores):
				  self.predicted_IPC[core].append(float(line_splitted[5*core+3]))  #offset=3  in the file 


      ######## kalmanOut_stall_time   
      self.Rfile_kalmanOut_stall_time = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_stall_time), 'r')
      line_count=-1
      for line in self.Rfile_kalmanOut_stall_time:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count>=2) and (line_count == total_line_count): 
              for core in range(sim.config.ncores):
				  self.predicted_stall_time[core].append(float(line_splitted[5*core+3]))  #offset=3  in the file 
      '''
      ######## kalmanOut_cpu_busy_time   
      self.Rfile_kalmanOut_cpu_busy_time = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_cpu_busy_time), 'r')
      line_count=-1
      for line in self.Rfile_kalmanOut_cpu_busy_time:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count>=2) and (line_count == total_line_count): 
              for core in range(sim.config.ncores):
				  self.predicted_cpu_busy_time[core].append(float(line_splitted[5*core+3]))  #offset=3  in the file 

      ''' 
      ######## kalmanOut_CPI   
      self.Rfile_kalmanOut_CPI = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_CPI), 'r')
      line_count=-1
      for line in self.Rfile_kalmanOut_CPI:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count>=2) and (line_count == total_line_count): 
              for core in range(sim.config.ncores):
				  self.predicted_CPI[core].append(float(line_splitted[5*core+3]))  #offset=3  in the file 
     
      ######## kalmanOut_L3_uncore_time   
      self.Rfile_kalmanOut_L3_uncore_time = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_L3_uncore_time), 'r')
      line_count=-1
      for line in self.Rfile_kalmanOut_L3_uncore_time:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count>=2) and (line_count == total_line_count): 
              for core in range(sim.config.ncores):
				  self.predicted_L3_uncore_time[core].append(float(line_splitted[5*core+3]))  #offset=3  in the file 
      '''      

      ######## kalmanOut_Workload   
      #self.Rfile_kalmanOut_Workload = file(os.path.join(sim.config.output_dir, self.filename_kalmanOut_Workload), 'r')
      #line_count=-1
      #for line in self.Rfile_kalmanOut_Workload:
      #    print line
      #    line_splitted = line.split('\t')
      #    line_count+=1
      #    print line_count
      #    print total_line_count
      #    print "YEYEYEYEYE"
      #    if (line_count>=2) and (line_count == total_line_count-1):# -1 
      #        print "yes"
      #        for core in range(sim.config.ncores):
	  #			  self.predicted_Workload[core].append(float(line_splitted[5*core+3]))  #offset=3  in the file 




      print "last predictions for core 0: "
      #print "CoreIns: %s"%self.predicted_CoreIns[0][self.num_snapshots-1]
      #print "IdleTimePerc: %s"%self.predicted_IdleTimePerc[0][self.num_snapshots-1]
      #print "IPC: %s"%self.predicted_IPC[0][self.num_snapshots-1]
      #print "cpu_cpu_busy_time: %s"%self.predicted_cpu_busy_time[0][self.num_snapshots-1] 
      #print "cpu_stall_time: %s"%self.predicted_stall_time[0][self.num_snapshots-1]
      #print "L3_uncore_time: %s"%self.predicted_L3_uncore_time[0][self.num_snapshots-1] 
      #print "CPI: %s"%self.predicted_CPI[0][self.num_snapshots-1] 
      #print "Workload: %s"%self.predicted_Workload[0][self.num_snapshots-2]
      #raw_input()
      
          
      ##############################################################
      ################# DVFS #######################################
      if self.DVFS:
          FreqList=['1000','1100','1200','1300','1400','1500','1600','1700','1800','1900','2000']
          AllowedPerformanceLoss= 0.05
          T=self.interval
          self.fd.write('%u' % (time / 1e6)) # Time in ns
          #currrent_freq = sim.dvfs.get_frequency(0)
          #currrent_freq -= 100

          #self.TotalWork+=1
          T_base=150
          for core in range(sim.config.ncores):
              freq_P = sim.dvfs.get_frequency(core)
              CPI_P = CPI[core]
              I_P = CoreIns[core]
              #self.T_delay[core] += ((I_P*(freq_H/freq_P-1)*CPI_P)/freq_H)
              #self.T_ref[core] += (I_P*CPI_P)/freq_P
              CpuBusyTime = cpu_busy_time[core]
              busy_time = 1-self.IdleTimePerc[core]
              self.T_delay[core] += (freq_H/freq_P-1)*CpuBusyTime
              self.T_ref[core] += busy_time


              print ("delay = %s     ref = %s     T= %s \n"%(   (freq_H/freq_P-1)*CpuBusyTime  ,  busy_time    ,   (self.interval/1000000) )  )
              self.T_delay_corrected[core] = self.T_delay[core] - (I_P*(freq_H/freq_P-1)*CPI_P)/freq_H # just to collect DNN data_set
              self.T_ref_corrected[core] = self.T_ref[core] - (I_P*CPI_P)/freq_P
              self.sum_inst[core] += CoreIns[core]


              if self.T_ref[core]==0:
                 self.PF[core] = 0
              else: 
                 self.PF[core]=self.T_delay[core]/self.T_ref[core]
              #print "PF[%d]=%s"%(core,self.PF[core])
              #print "PF[%d]=%s, delay=%s, ref=%s, freq=%s"%(core,self.PF[core],self.T_delay[core],self.T_ref[core],freq_P)
              #raw_input()

              #self.TotalInstDone[core]+= CoreIns[core]*(2000.0/sim.dvfs.get_frequency(core)) 
              self.TotalInstDone[core]+= CoreIns[core] 
              if   (self.TotalInstDone[core]!=0):
                   self.InstLoss[core] = CoreIns[core]*(freq_H/freq_P-1)
                   self.InstDone[core] = CoreIns[core]
                   self.InstLossRate[core] = (1-(sim.dvfs.get_frequency(core)/2000.0))
                   self.Inst_for_freq_H[core] = CoreIns[core]*(freq_H/freq_P)

                   self.TotalInst_for_freq_H[core]+=self.Inst_for_freq_H[core]
                   self.TotallInstLoss[core]+=CoreIns[core]*(1-(sim.dvfs.get_frequency(core)/2000.0))
                   self.TotallInstDone[core]+=CoreIns[core]         
                   self.TotalInstLossRate[core]=self.TotallInstLoss[core]/self.TotalInstDone[core]
              #self.ExpectedWorkDone[core]+=(2000/sim.dvfs.get_frequency(core))
              #ExpectedRemainedWork[core]=TotalWork-ExpectedWorkDone[core]              
              self.fd.write(' f: %.2fGHz' %(sim.dvfs.get_frequency(core)/1000.0))
          #raw_input()



          ##################correction###################(just to record frequencies for the DNN. does not set them)
          ################################################
          for core in range(sim.config.ncores):
            '''
            I_prev_corrected = CoreIns[core]
            try:
                     average_inst_corrected = ((self.sum_inst[core]-I_prev_corrected)/(self.num_snapshots-1))
            except:
                     average_inst_corrected = 0

            print ("average_inst_corrected=%f\n"%average_inst_corrected)
            print ("I_prev_corrected=%f\n"%I_prev_corrected)

            if (average_inst_corrected>2*I_prev_corrected):
                   if (sim.dvfs.get_frequency(core)-100)>=1000:
                      self.freq_corrected[core]=(sim.dvfs.get_frequency(core)-100)
                   else:
                      self.freq_corrected[core]=1000

            elif (average_inst_corrected<0.5*I_prev_corrected):
                   if (sim.dvfs.get_frequency(core)+100)<=2000:
                      self.freq_corrected[core]=(sim.dvfs.get_frequency(core)+100)
                   else:
                      self.freq_corrected[core]=2000
            
            else:
            '''
            freq_set=0
            for freq in FreqList:#from low freq to high freq

                         freq_prev_corrected=float(freq)
                         if (freq_set==0):
                                CPI_prev_corrected = CPI[core]
                                I_prev_corrected = CoreIns[core]
                                ### down was commented 
                                #self.T_delay_prev_corrected[core] = (I_prev_corrected*CPI_prev_corrected)*(freq_H/freq_prev_corrected-1)/freq_H + self.T_delay_corrected[core]
                                #self.T_ref_prev_corrected[core] = (I_prev_corrected*CPI_prev_corrected)/freq_prev_corrected + self.T_ref_corrected[core]#(self.interval/1000000)/freq_H #*CPI_prev_corrected)
                                #self.T_ref_prev_corrected[core] = T_base + self.T_ref_corrected[core]#(self.interval/1000000)/freq_H #*CPI_prev_corrected)

                                #self.T_delay_prev_corrected[core] = (I_prev_corrected*CPI_prev_corrected)*(freq_H/freq_prev_corrected-1)/freq_H #+ self.T_delay_corrected[core]
                                #self.T_ref_prev_corrected[core] = (average_inst_corrected*CPI_prev_corrected)/freq_prev_corrected #+ self.T_ref_corrected[core]#(self.interval/1000000)/freq_H 
                                ### up was commented
                                busyTime_prev_corrected = 1-self.IdleTimePerc[core] 
                                cpu_busy_prev_corrected = cpu_busy_time[core]

                                self.T_delay_prev_corrected[core] = cpu_busy_prev_corrected*(freq_H/freq_prev_corrected-1) + self.T_delay[core]
                                self.T_ref_prev_corrected[core] = busyTime_prev_corrected + self.T_ref[core]
                                   

                                if self.T_ref_prev_corrected[core]==0:
                                     self.PF_prev_corrected[core] = 0
                                else: 
                                     self.PF_prev_corrected[core]=(self.T_delay_prev_corrected[core]/self.T_ref_prev_corrected[core])

                                                               
                                
                                print "PF_next[%d]=%s,delay=%s,ref=%s,freq_next=%s"%(core,self.PF_prev_corrected[core],self.T_delay_prev_corrected[core],self.T_ref_prev_corrected[core],freq_prev_corrected)

                                #if (self.PredictedTotalInstLossRate[core] < AllowedPerformanceLoss):
                                if (self.PF_prev_corrected[core] < AllowedPerformanceLoss):
                                     self.freq_corrected[core]=int(freq_prev_corrected)
                                     freq_set=1 


            if (freq_set==0):#any of the frequencies not proper. we use the highest not to let the loss increase
                        self.freq_corrected[core]=int(freq_H)





          ##############SummaryDVFS##############################################################
          self.Wfile_SummaryDVFS = file(os.path.join(sim.config.output_dir, self.filename_SummaryDVFS), 'a')
          self.Wfile_SummaryDVFS.write('\n')
          self.Wfile_SummaryDVFS.write('%d\t'%(self.num_snapshots))
          self.Wfile_SummaryDVFS.write('CoreIns')
          for core in range(sim.config.ncores):
               self.Wfile_SummaryDVFS.write("\t\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t"%(core,sim.dvfs.get_frequency(core),self.freq_corrected[core],self.InstDone[core],\
                          self.PredictedInstDone[core],self.Inst_for_freq_H[core],self.PredictedInst_for_freq_H[core],self.InstLoss[core],\
                          self.PredictedInstLoss[core],self.InstLossRate[core],self.PredictedInstLossRate[core],self.TotallInstDone[core],\
                          self.PredictedTotalInstDone[core],self.TotalInstLossRate[core],self.PredictedTotalInstLossRate[core],self.PF[core],self.PF_next[core]))          
          self.Wfile_SummaryDVFS.close()

          ##############Frequencies##############################################################
          self.Wfile_Frequencies = file(os.path.join(sim.config.output_dir, self.filename_Frequencies), 'a')
          self.Wfile_Frequencies.write('\n')
          self.Wfile_Frequencies.write('%d\t'%(self.num_snapshots))
          for core in range(sim.config.ncores):
               self.Wfile_Frequencies.write('%s\t%s\t'%(sim.dvfs.get_frequency(core),self.freq_corrected[core]))    
          self.Wfile_Frequencies.close()

          ########################################################################################
          for core in range(sim.config.ncores):
            if (self.num_snapshots>2) :
              '''
              I_P_next = self.predicted_CoreIns[core][self.num_snapshots-1]
              I_P_current = CoreIns[core]
              if (I_P_next<I_P_current):
                   if (sim.dvfs.get_frequency(core)-100)>=1000:
                      sim.dvfs.set_frequency(core,(sim.dvfs.get_frequency(core)-100))
                   else:
                      sim.dvfs.set_frequency(core,1000)
              if (I_P_next>I_P_current):                      
                   if (sim.dvfs.get_frequency(core)+100)<=2000:
                      sim.dvfs.set_frequency(core,(sim.dvfs.get_frequency(core)+100))
                   else:
                      sim.dvfs.set_frequency(core,2000)

              else:
              '''
              ''' 
              I_P_next = self.predicted_CoreIns[core][self.num_snapshots-1]
                 I_prev_corrected = CoreIns[core]
                 try:
                     average_inst_pred = ((self.sum_inst[core])/(self.num_snapshots))
                 except:
                     average_inst_pred = 0
                 print ("average_inst_done=%f\n"%average_inst_pred)
                 print ("I_p_next=%f\n"%I_P_next)

                 if (average_inst_pred>2*I_P_next):
                   if (sim.dvfs.get_frequency(core)-100)>=1000:
                      sim.dvfs.set_frequency(core,(sim.dvfs.get_frequency(core)-100))
                   else:
                      sim.dvfs.set_frequency(core,1000)

                 elif (average_inst_pred<0.5*I_P_next):
                   if (sim.dvfs.get_frequency(core)+100)<=2000:
                      sim.dvfs.set_frequency(core,(sim.dvfs.get_frequency(core)+100))
                   else:
                      sim.dvfs.set_frequency(core,2000)

                 else:
              '''   



              ################################################ (DVFS engine)
              ################################################ (DVFS engine)
              
	      freq_set=0
  	      for freq in FreqList:#from low freq to high freq
                         freq_P_next=float(freq)
                         if (freq_set==0):
                                #CPI_P_next = self.predicted_CPI[core][self.num_snapshots-1]
                                #I_P_next = self.predicted_CoreIns[core][self.num_snapshots-1]

                                #self.T_delay_next[core] = (I_P_next*(freq_H/freq_P_next-1)*CPI_P_next)/freq_H + self.T_delay[core]
                                #self.T_ref_next[core] = (I_P_next*CPI_P_next)/freq_P_next + self.T_ref[core]
                                
                                #for Kalman
                                #busyTime_P_next = (1-self.predicted_IdleTimePerc[core][self.num_snapshots-1])
                                #cpu_busy_time_P_next = self.predicted_cpu_busy_time[core][self.num_snapshots-1]

                                #for LSTM
                                busyTime_P_next = (1-float(LSTM_pred_IdleTimePerc[core]))
                                cpu_busy_time_P_next = float(LSTM_pred_CPU_busy_time[core])


                                self.T_delay_next[core] = cpu_busy_time_P_next*(freq_H/freq_P_next-1) + self.T_delay[core]
                                self.T_ref_next[core] = busyTime_P_next + self.T_ref[core]



                                #self.T_ref_next[core] = T_base + self.T_ref[core]
                                if self.T_ref_next[core]==0:
                                     self.PF_next[core] = 0
                                else: 
                                     self.PF_next[core]=self.T_delay_next[core]/self.T_ref_next[core]

                                print "PF_next[%d]=%s,delay=%s,ref=%s,freq_next=%s"%(core,self.PF_next[core],self.T_delay_next[core],self.T_ref_next[core],freq_P_next)
                                #raw_input()
                                ### down was commented 
                                self.PredictedInstLoss[core] = int(self.predicted_CoreIns[core][self.num_snapshots-1])*(freq_H/freq_P_next-1)
                                self.PredictedInstDone[core] = self.predicted_CoreIns[core][self.num_snapshots-1]
                                self.PredictedInst_for_freq_H[core] = self.predicted_CoreIns[core][self.num_snapshots-1]*(freq_H/freq_P_next)
                                if self.PredictedInstDone[core]==0 :
                                      self.PredictedInstLossRate[core]=0
                                else:
                                      self.PredictedInstLossRate[core] = float(self.PredictedInstLoss[core])/self.PredictedInstDone[core]
                                self.PredictedTotalInst_for_freq_H[core] = self.PredictedInst_for_freq_H[core] + self.TotalInst_for_freq_H[core]
                                self.PredictedTotalInstLoss[core] =  self.PredictedInstLoss[core] + self.TotallInstLoss[core]
                                self.PredictedTotalInstDone[core] = self.PredictedInstDone[core] + self.TotalInstDone[core]
                                if (self.PredictedTotalInstDone[core]==0):
                                         self.PredictedTotalInstLossRate[core]=0
                                else:
                                         self.PredictedTotalInstLossRate[core] = float(self.PredictedTotalInstLoss[core])/self.PredictedTotalInstDone[core]
                                ### up was commented
                                #if (self.PredictedTotalInstLossRate[core] < AllowedPerformanceLoss):
                                if (self.PF_next[core] < AllowedPerformanceLoss):
                                     sim.dvfs.set_frequency(core,int(freq_P_next))
                                     freq_set=1 

  	      if (freq_set==0):#any of the frequencies not proper. we use the highest not to let the loss increase
    	                sim.dvfs.set_frequency(core,int(freq_H))
  	              #if (core==0)or(core==4)or(core==8)or(core==12):
  	              #if (core==0):
     	          #      sim.dvfs.set_frequency(core,5000)

  	         #if ((self.num_snapshots) ==10)or((self.num_snapshots) ==20):
                 #            sim.dvfs.set_frequency(core,int(freq_H))





		      
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
          #raw_input()
      ############################################################## 
      #os.system("/home/milad/sniper/tools/dumpstats.py --partial periodic-%d:periodic-%d | grep power.Core"%( ((self.num_snapshots-1) *self.interval), ((self.num_snapshots) *self.interval ) ) )

      #raw_input(); #getch
      self.fd.write('periodic-%d' % (self.num_snapshots * self.interval))      

      #periodic stat in stats file
      #gen_simout.generate_simout(resultsdir = sim.config.output_dir, partial = ('periodic-%d' % ((self.num_snapshots-1) *self.interval), 'periodic-%d' % ((self.num_snapshots) *self.interval ) ), output = open(os.path.join(sim.config.output_dir, 'stats/p%d.out'%self.num_snapshots), 'w'), silent = True)
      #gen_simout.generate_simout(resultsdir = sim.config.output_dir, partial = ('periodic-10000000000','periodic-20000000000'), output = open(os.path.join(sim.config.output_dir, 'stats/p%d.out'%self.num_snapshots), 'w'), silent = True)

      self.next_interval += self.interval



sim.util.register(PeriodicStats())
