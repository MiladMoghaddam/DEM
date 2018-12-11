"""
periodic-stats.py

Periodically write out all statistics
1st argument is the interval size in nanoseconds (default is 1e9 = 1 second of simulated time)
2rd argument, if present will limit the number of snapshots and dynamically remove itermediate data
"""

import user_level as UL
sniper_path = UL.get_sniper_path()

print sniper_path

import sim, os, sys

sys.path.insert(0, '%s/tools/'%sniper_path)
import sniper_lib
import gen_simout

import DNN_feature_collector as DFC


#############################################

#############################################
#######################################################################################################
# look at /sniper/scripts/user_level.py
FreqList=['1000','1100','1200','1300','1400','1500','1600','1700','1800','1900','2000']

W_P=UL.get_window_past()
freq_w = [] #a window of last frequency values
for i in range(W_P):
    freq_w.append([])
for i in range(W_P):
   for core in range(sim.config.ncores):
      freq_w[i].append(2000.0) #defult frequency
######################################################
class PeriodicStats:
  def setup(self, args):
    args = dict(enumerate((args or '').split(':')))
    interval = long(args.get(0, '') or 1000000000)

    self.DVFS = 1
    self.CMP_based_DNN_flag = 0
    self.W_P=UL.get_window_past()
    self.freq_w = [] #a window of last frequency values

    for i in range(self.W_P):
        self.freq_w.append([])

    for i in range(self.W_P):
       for core in range(sim.config.ncores):
          self.freq_w[i].append(2000.0) #defult frequency    

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
    if not os.path.exists("%s/outfiles"%sniper_path):
    	os.makedirs("%s/outfiles"%sniper_path, 0777)

    filename="statsPeriodic.txt"
    self.fd = file(os.path.join(sim.config.output_dir, filename), 'w')         

    #############################
    self.filename_DNN_feature_label = 'DNN_feature_label.csv'
    self.filename_DNN_frequencies = 'DNN_frequencies.xls'
    self.Wfile_DNN_frequencies = file(os.path.join(sim.config.output_dir, self.filename_DNN_frequencies), 'a')
    self.Wfile_DNN_frequencies.write("Interval\t")
    for core in range(sim.config.ncores):
        self.Wfile_DNN_frequencies.write("%s\t"%core)        
    self.Wfile_DNN_frequencies.write("\n") 
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
      current_freqs = []      
      for core in range(sim.config.ncores):
            current_freqs.append(sim.dvfs.get_frequency(core))

      W_P = self.W_P
      for w in (range(1,W_P)):
          self.freq_w[w-1]=self.freq_w[w]
      self.freq_w[W_P-1]= current_freqs

      feature_list = DFC.collect_online_window_based(self.num_snapshots,sim.config.output_dir,sim.config.ncores,self.freq_w)
      print feature_list
      #################### DNN_frequencies ##########################################
      self.Wfile_DNN_frequencies = file(os.path.join(sim.config.output_dir, self.filename_DNN_frequencies), 'a')
      self.Wfile_DNN_frequencies.write("%s\t"%self.num_snapshots)
      for core in range(sim.config.ncores):      
          self.Wfile_DNN_frequencies.write("%s\t"%current_freqs[core])
      self.Wfile_DNN_frequencies.write("\n")
      self.Wfile_DNN_frequencies.close() 
      print "\n1\n"
      ##############################################################
      ################# DVFS #######################################
      if self.DVFS:
          print "\n2\n"
          AllowedPerformanceLoss= 0.05
          freq_H = 2000.0
          T=self.interval
          self.fd.write('%u' % (time / 1e6)) # Time in ns
          ########################################################################################
          if (self.CMP_based_DNN_flag):
              print "\n3\n"
              features = []
              last_freq = current_freqs # to be compatible with feature_list
              for core in range(sim.config.ncores):
                  for f in feature_list:      
                      features.append(f[core]) 
              print ('features= %s'%features)
              #os.system ("%s/scripts/DNN_predict.py %s %s"%(sniper_path, features, os.path.join(sim.config.output_dir, self.predicted_freq)))

          ########################################################################################
          if (self.CMP_based_DNN_flag==0): # core based DNN, 
                  print "\n4\n"
                  to_predictor = ''
                  for core in range(sim.config.ncores):
                      features = []
                      for f in feature_list:
                          features.append(f[core])
                      for l in range (len(features)-1):
                          # I pass a list of features for all the cores, seperated by ',' between each feature
                          # and seperated by '*' for each cores
                          # f1,f2,f3,f4,f5*f1,f2,f3,f4,f5*f1,f2,f3,f4,f5 ... 
                          to_predictor = '%s%s,'%(to_predictor,features[l])
                      to_predictor = '%s%s*'%(to_predictor,features[len(features)-1])
                  #note to myself: I called it using os.system to prevent errors generated because of having different numpy versions 
                  print "... DNN predicting ...(sniper/sniper/scripts!!!\n"
                  #print ("python %s/scripts/DNN_predict.py %s %s\n"%(sniper_path,to_predictor,os.path.join(sim.config.output_dir,'predictions.txt')))
                  #predictions = os.system ("python %s/scripts/DNN_predict.py %s %s"%(sniper_path,to_predictor,os.path.join(sim.config.output_dir,'predictions.txt')))

                  Wfile_predictor_arg = file(os.path.join(sim.config.output_dir,'arg.txt'),'w')
                  Wfile_predictor_arg.write ('%s'%to_predictor)
                  Wfile_predictor_arg.close()
                  predictions = os.system ("python %s/scripts/DNN_predict.py %s %s"%(sniper_path,os.path.join(sim.config.output_dir,'arg.txt'),os.path.join(sim.config.output_dir,'predictions.txt')))            

          #################### feature_label  ###########################################
          self.Wfile_DNN_feature_label = file(os.path.join(sim.config.output_dir, self.filename_DNN_feature_label), 'a')
          for core in range(sim.config.ncores):      
                features = []
                for f in feature_list:
                    features.append(f[core])
                for l in range (len(features)):
                    self.Wfile_DNN_feature_label.write("%s,"%features[l])
                self.Wfile_DNN_feature_label.write("%s\n"%UL.translate_freq_to_class(current_freqs[core]))
          self.Wfile_DNN_feature_label.close()     
          print "\n5\n"
          ######################## Read DNN predicted frequencies from file generated by DNN ######
          Rfile_DNN_pred = file(os.path.join(sim.config.output_dir,'predictions.txt'),'r')
          DNN_pred_freq = []
          print ("predicted Frequencies by DNN:\n")
          line_count=-1
          for line in Rfile_DNN_pred:
              line_count+=1
              DNN_pred_freq.append(int(line))
              print ("core[%s]=%s"%(line_count,int(line)))
          Rfile_DNN_pred.close()

          for core in range(sim.config.ncores):              
              
              sim.dvfs.set_frequency(core,DNN_pred_freq[core])


              cycles = (self.stats['time'][core].delta - self.stats['ffwd_time'][core].delta) * sim.dvfs.get_frequency(core) / 1e9 # convert fs to cycles
              instrs = self.stats['instrs'][core].delta
              ipc = instrs / (cycles or 1) # Avoid division by zero


              # include fast-forward IPCs
              cycles = self.stats['time'][core].delta * sim.dvfs.get_frequency(core) / 1e9 # convert fs to cycles
              instrs = self.stats['coreinstrs'][core].delta
              ipc = instrs / (cycles or 1)
              self.fd.write(' %.3f' % ipc)
          self.fd.write('\n')
      ############################################################## 
      self.fd.write('periodic-%d' % (self.num_snapshots * self.interval))  
      print  ('periodic-%d' % (self.num_snapshots * self.interval))     
      
      self.next_interval += self.interval



sim.util.register(PeriodicStats())
