import sys,os
sys.path.insert(0, '/home/milad/sniper/tools/')
import sniper_lib
sys.path.insert(0, '/home/milad/sniper/tf/')
import user_level as UL
# I have placed this file in $sniper/scripts/
# This file has two main functions
# 1: collect_offline(...) which is called by DNN_offline_datacollector.py or in my work bash.sh (in directories that we want to extract features from sqlite and SumamryDVFS.txt)
#    return features,freq   (to the porpuse of training the DNN)

# 2: collect_online(...) which is called by DNN_predict_VF.py (inside $sniper/scripts/ )
#    returns features       (to the porpuse of feeding the DNN to predict the freq)

interval = 1000000000000 #equal to 1000000 

def get_stats(line_count,benchmark_dir,num_core,mode,mode_param1,mode_param2):
              #online_freq just works with collect_online and for collect_offline, the freq is read from SummaryDVFS.txt 
              # if mode = 'OFFLINE'
              #     mode_param1 contains line_splitted of previous frequencies
              #     mode_param2 contains line_splitted of current frequencies
              # if mode = 'ONLINE'
              #     mode_param1 contains freqs      
              #     mode_param2 contains freqs

              print ("stats for %s"%line_count)

              stall_time = []
              freq = []
              freq_class = []
              previous_freq = []
              previous_freq_class = []

              stall = []
              L3_uncore_time = []
              IPC = []
              cpu_busy_time = []
              IdleTimePerc = []

              for core in range(0,num_core):
                  freq.append(0.0)
                  freq_class.append(-1)
                  previous_freq.append(0.0)
                  previous_freq_class.append(-1)
                  stall_time.append(0.0)
                  stall.append(0)
                  IPC.append(0.0)
                  L3_uncore_time.append(0.0)
                  cpu_busy_time.append(0.0)
                  IdleTimePerc.append(0.0)
              
              partial = ('periodic-%d' %((line_count-1) *interval), 'periodic-%d' % ((line_count) *interval ) )
              #try: 
              results = sniper_lib.get_results(resultsdir = benchmark_dir , partial = ('periodic-%d' %((line_count-1) *interval), 'periodic-%d' % ((line_count) *interval ) ))['results']
              #except:
              #    return 'TRASH',0 #return class 0 as the label

              CoreIns = results['core.instructions']
              IdleTime= results['performance_model.idle_elapsed_time']
              BusyTime= results['performance_model.nonidle_elapsed_time']
              CycleCount= results['performance_model.cycle_count']
              TotalTime= results['performance_model.elapsed_time']
              Futex= results['performance_model.cpiSyncFutex']
              L3_uncore_total_time= results['L3.uncore-totaltime']
              cpu_base_time= results['interval_timer.cpiBase']

              cpContr_branch= results['interval_timer.cpContr_branch']
              cpContr_fp_addsub= results['interval_timer.cpContr_fp_addsub']
              cpContr_fp_muldiv= results['interval_timer.cpContr_fp_muldiv']

              uop_branch= results['interval_timer.uop_branch']
              uop_fp_addsub= results['interval_timer.uop_fp_addsub']
              uop_fp_muldiv= results['interval_timer.uop_fp_muldiv']
              uop_generic= results['interval_timer.uop_generic']
              uop_load= results['interval_timer.uop_load']
              uop_store= results['interval_timer.uop_store']


              '''  
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
              ''' 
             
              format_int = lambda v: str(long(v))
              format_pct = lambda v: '%.1f%%' % (100. * v)
              def format_float(digits):
                  return lambda v: ('%%.%uf' % digits) % v
              def format_ns(digits):
                  return lambda v: ('%%.%uf' % digits) % (v/1e6)

              ########## tlb ##########################
              for tlb in ('itlb', 'dtlb', 'stlb'): 
                  results['%s.missrate'%tlb] = map(lambda (a,b): 100*a/float(b or 1), zip(results['%s.miss'%tlb], results['%s.access'%tlb]))
                  results['%s.mpki'%tlb] = map(lambda (a,b): 1000*a/float(b or 1), zip(results['%s.miss'%tlb], results['performance_model.instruction_count']))
              
              itlb_missrate= results['itlb.missrate']
              dtlb_missrate= results['dtlb.missrate']
              stlb_missrate= results['stlb.missrate']
              itlb_miss= results['itlb.miss']
              dtlb_miss= results['dtlb.miss']
              stlb_miss= results['stlb.miss']
              itlb_access= results['itlb.access']
              dtlb_access= results['dtlb.access']
              stlb_access= results['stlb.access']
              itlb_mpki= results['itlb.mpki']
              dtlb_mpki= results['dtlb.mpki']
              stlb_mpki= results['stlb.mpki']

              ######## branch_predictor ##########
              results['branch_predictor.missrate'] = [ 100 * float(results['branch_predictor.num-incorrect'][core])
                     / ((results['branch_predictor.num-correct'][core] + results['branch_predictor.num-incorrect'][core]) or 1) for core in range(num_core) ]
              results['branch_predictor.mpki'] = [ 1000 * float(results['branch_predictor.num-incorrect'][core])
                     / (results['performance_model.instruction_count'][core] or 1) for core in range(num_core) ]

              branch_predictor_missrate= results['branch_predictor.missrate']
              branch_predictor_num_incorrect= results['branch_predictor.num-incorrect']
              branch_predictor_num_correct= results['branch_predictor.num-correct']
              branch_predictor_mpki= results['branch_predictor.mpki']

              ######## cache ##########
              allcaches = [ 'L1-I', 'L1-D' ] + [ 'L%u'%l for l in range(2, 5) ]
              existcaches = [ c for c in allcaches if '%s.loads'%c in results ]

              for c in existcaches:
                results['%s.accesses'%c] = map(sum, zip(results['%s.loads'%c], results['%s.stores'%c]))
                results['%s.misses'%c] = map(sum, zip(results['%s.load-misses'%c], results.get('%s.store-misses-I'%c, results['%s.store-misses'%c])))
                results['%s.missrate'%c] = map(lambda (a,b): 100*a/float(b) if b else float('inf'), zip(results['%s.misses'%c], results['%s.accesses'%c]))
                results['%s.mpki'%c] = map(lambda (a,b): 1000*a/float(b) if b else float('inf'), zip(results['%s.misses'%c], results['performance_model.instruction_count']))
            
              L1_I_missrate= results['L1-I.missrate']
              L1_I_accesses= results['L1-I.accesses']
              L1_I_misses= results['L1-I.misses']
              L1_I_load_accesses= results['L1-I.loads']
              L1_I_store_accesses= results['L1-I.stores']
              L1_I_load_misses= results['L1-I.load-misses']
              L1_I_store_misses= results.get('L1-I.store-misses-I', results['L1-I.store-misses'])

              L1_D_missrate= results['L1-D.missrate']
              L1_D_accesses= results['L1-D.accesses']
              L1_D_misses= results['L1-D.misses']
              L1_D_load_accesses= results['L1-D.loads']
              L1_D_store_accesses= results['L1-D.stores']
              L1_D_load_misses= results['L1-D.load-misses']
              L1_D_store_misses= results.get('L1-D.store-misses-I', results['L1-D.store-misses'])

              L2_missrate= results['L2.missrate']
              L2_accesses= results['L2.accesses']
              L2_misses= results['L2.misses']
              L2_load_accesses= results['L2.loads']
              L2_store_accesses= results['L2.stores']
              L2_load_misses= results['L2.load-misses']
              L2_store_misses= results.get('L2.store-misses-I', results['L2.store-misses'])
		  
              L3_missrate= results['L3.missrate']
              L3_accesses= results['L3.accesses']
              L3_misses= results['L3.misses']
              L3_load_accesses= results['L3.loads']
              L3_store_accesses= results['L3.stores']
              L3_load_misses= results['L3.load-misses']
              L3_store_misses= results.get('L3.store-misses-I', results['L3.store-misses'])       

              ######### dram #####################################
              results['dram.accesses'] = map(sum, zip(results['dram.reads'], results['dram.writes']))
              results['dram.avglatency'] = map(lambda (a,b): a/b if b else float('inf'), zip(results['dram.total-access-latency'], results['dram.accesses']))

              dram_accesses= results['dram.accesses']
              dram_reads= results['dram.reads']
              dram_writes= results['dram.writes']
              ####################################################
              for core in range(0,num_core):
                  #print ('core:%s'%core)
                  #print ('core:%s'%num_core)
                  if (mode == 'OFFLINE'):
                     #freq[core] = float(mode_param[18*core+4]) #old version (for SummaryDVFS.xls)
                     previous_freq[core] = float(mode_param1[2*core+2])
                     previous_freq_class[core] = UL.translate_freq_to_class(int(previous_freq[core]))
                     freq[core] = float(mode_param2[2*core+2])
                     freq_class[core] = UL.translate_freq_to_class(int(freq[core]))
                  elif (mode == 'ONLINE'):
                     freq[core]=mode_param1[core]
                     freq_class[core] = UL.translate_freq_to_class(int(freq[core]))

                  ''' 
                  for name in stall_list:
                     stall_temp= results['interval_timer.%s'%name]                     
                     stall[core]+=stall_temp[core] 

                  stall_time[core] = float(stall[core]) / TotalTime[core]
                  cpu_busy_time[core] = 1-(IdleTimePerc[core]+stall_time[core])
                  '''
                  L3_uncore_time[core] =  float(L3_uncore_total_time[core])/TotalTime[core] 
                  IPC[core] = (int(CoreIns[core])/((freq[core]/1000.0)*(interval/1000000)))              
                  IdleTimePerc[core]=float(IdleTime[core])/float(TotalTime[core])
                  if (IdleTimePerc[core]<0):
                      IdleTimePerc[core]=0.0



              #features: 
              #         CoreIns,IPC,IdleTimePerc,IdleTime,BusyTime,CycleCount,TotalTime,cpu_base_time,L3_uncore_time,Futex
              #         itlb_missrate,itlb_miss,itlb_access,itlb_mpki,
              #         dtlb_missrate,dtlb_miss,dtlb_access,dtlb_mpki,
              #         stlb_missrate,stlb_miss,stlb_access,stlb_mpki,
              #         branch_predictor_missrate,branch_predictor_num_incorrect,branch_predictor_num_correct,branch_predictor_mpki
              #         L1_I_missrate,L1_I_accesses,L1_I_load_accesses,L1_I_load_accesses,L1_I_store_accesses,L1_I_load_misses,L1_I_store_misses
              #         L1_D_missrate,L1_D_accesses,L1_D_load_accesses,L1_D_load_accesses,L1_D_store_accesses,L1_D_load_misses,L1_D_store_misses
              #         L2_missrate,L2_accesses,L2_load_accesses,L2_load_accesses,L2_store_accesses,L2_load_misses,L2_store_misses
              #         L3_missrate,L3_accesses,L3_load_accesses,L3_load_accesses,L3_store_accesses,L3_load_misses,L3_store_misses
              #         cpContr_branch,cpContr_fp_addsub,cpContr_fp_muldiv
              #         uop_branch,uop_fp_addsub,uop_fp_muldiv,uop_generic,uop_load,uop_store

              #feature_list = [CoreIns,IPC,IdleTimePerc,L3_uncore_time,L1_I_missrate,L1_D_missrate,uop_fp_addsub,uop_fp_muldiv]
              #feature_list = [CoreIns,IPC,IdleTimePerc,IdleTime,BusyTime,CycleCount]
              ''' 
              feature_list = [CoreIns,IPC,IdleTimePerc,IdleTime,BusyTime,CycleCount,TotalTime,cpu_base_time,L3_uncore_time,Futex,
                              itlb_missrate,itlb_miss,itlb_access,itlb_mpki,
                              dtlb_missrate,dtlb_miss,dtlb_access,dtlb_mpki,
                              stlb_missrate,stlb_miss,stlb_access,stlb_mpki,
                              branch_predictor_missrate,branch_predictor_num_incorrect,branch_predictor_num_correct,branch_predictor_mpki,
                              L1_I_missrate,L1_I_accesses,L1_I_load_accesses,L1_I_load_accesses,L1_I_store_accesses,L1_I_load_misses,L1_I_store_misses,
                              L1_D_missrate,L1_D_accesses,L1_D_load_accesses,L1_D_load_accesses,L1_D_store_accesses,L1_D_load_misses,L1_D_store_misses,
                              L2_missrate,L2_accesses,L2_load_accesses,L2_load_accesses,L2_store_accesses,L2_load_misses,L2_store_misses,
                              L3_missrate,L3_accesses,L3_load_accesses,L3_load_accesses,L3_store_accesses,L3_load_misses,L3_store_misses,
                              cpContr_branch,cpContr_fp_addsub,cpContr_fp_muldiv,
                              uop_branch,uop_fp_addsub,uop_fp_muldiv,uop_generic,uop_load,uop_store]
              '''
              feature_list = [CoreIns,IPC,IdleTimePerc,IdleTime,BusyTime,CycleCount,TotalTime,cpu_base_time,L3_uncore_time,Futex,
                              itlb_missrate,itlb_miss,itlb_access,itlb_mpki,
                              dtlb_missrate,dtlb_miss,dtlb_access,dtlb_mpki,
                              stlb_missrate,stlb_miss,stlb_access,stlb_mpki,
                              branch_predictor_missrate,branch_predictor_num_incorrect,branch_predictor_num_correct,branch_predictor_mpki,
                              L1_I_missrate,L1_I_accesses,L1_I_load_accesses,L1_I_load_accesses,L1_I_store_accesses,L1_I_load_misses,L1_I_store_misses,
                              L1_D_missrate,L1_D_accesses,L1_D_load_accesses,L1_D_load_accesses,L1_D_store_accesses,L1_D_load_misses,L1_D_store_misses,
                              L2_missrate,L2_accesses,L2_load_accesses,L2_load_accesses,L2_store_accesses,L2_load_misses,L2_store_misses,
                              L3_missrate,L3_accesses,L3_load_accesses,L3_load_accesses,L3_store_accesses,L3_load_misses,L3_store_misses,
                              cpContr_branch,cpContr_fp_addsub,cpContr_fp_muldiv,
                              uop_branch,uop_fp_addsub,uop_fp_muldiv,uop_generic,uop_load,uop_store]
              

              #TODO
              for core in range(0,num_core):
                  for f in feature_list:
                      if f[core]== float('inf'):
                         #print "inf\n"
                         f[core]=10.0

              if (mode == 'OFFLINE'): #add freq as label                 
                 return  feature_list,previous_freq_class,freq_class

              if (mode == 'ONLINE'): #without freq as label                 
                 return  feature_list,freq # freq containes not the current freq but the previous freq

'''
def collect_offline(input_dir,input_filename,output_dir,output_filename,collect_mode): #collects the stats from sqlite files generated earlier

    Rfile_read_freq = file(os.path.join(input_dir, input_filename), 'r')
    Wfile_features_labels = file(os.path.join(output_dir,output_filename), 'a') 
    
    line_count=-1
    for line in Rfile_read_freq:
          line_splitted = line.split('\t')
          line_count+=1
          if (line_count==0):
              num_core = int(line_splitted[0])

          if (line_count>1):
              feature_list,labels = get_stats(line_count,input_dir,num_core,'OFFLINE',line_splitted)
              #print feature_list              
              if (collect_mode=='CORE_BASED'):
                  for core in range(num_core):  
                      for f in feature_list:                      
                          #print f[core]
                          Wfile_features_labels.write('%s,'%f[core])           
                      Wfile_features_labels.write('%s\n'%labels[core]) 

    Rfile_read_freq.close()  
    Wfile_features_labels.close()

def collect_online(current_run_period,benchmark_dir,ncore,freq): #during sniper runTime
     
     feature_list=get_stats(current_run_period,benchmark_dir,ncore,'ONLINE',freq) 
     return feature_list
'''


def collect_online_window_based(current_run_period,benchmark_dir,ncore,freq): #during sniper runTime
     W_P=UL.get_window_past()
     window_based_feature_list = []
     feature_list=[]
     for w in range (W_P):
         feature_list.append([])
     current_feature_list=get_stats(current_run_period,benchmark_dir,ncore,'ONLINE',freq,freq) 
     for w in reversed(range (W_P)): 
           offset=W_P-1-w         
           if current_run_period-offset>=1:
               feature_list[w]=get_stats(current_run_period-offset,benchmark_dir,ncore,'ONLINE',freq,freq) 
               last_feature_list = feature_list[w]
           else:
               feature_list[w]= last_feature_list             

     for w in range (W_P):
           window_based_feature_list+=feature_list[w]

     return window_based_feature_list
    


def collect_offline_window_based(input_dir,input_filename,output_dir,output_filename,collect_mode): #collects the stats from sqlite files generated earlier
    W_P=UL.get_window_past() #Window for Past sequences
    #TODO
    W_F=1 #UL.get_window_future() #Window for Future sequences # currently 1 step forward prediction, because the DNN just has one output
    print ("input_dir window based= %s\n"%input_dir)  
 
    Rfile_read_freq = file(os.path.join(input_dir, input_filename), 'r')
    Wfile_features_labels = file(os.path.join(output_dir,output_filename), 'a') 
    feature_list = []
    for w in range(0,W_P):
          feature_list.append([])
 
    line_count=-1

    #current_param = []
    #previous_param = []
    for line in Rfile_read_freq:
          line_splitted = line.split('\t')

          #previous_param = current_param  
          previous_param=line_splitted       
          current_param=line_splitted
 
          line_count+=1
          if (line_count==0):
              num_core = int(current_param[0])
              #for i in range(num_core*2+2):
              #      current_param[i]='2000' #default frequency                               

          if (line_count>W_P):
              if (collect_mode=='CORE_BASED'):
                 for w in reversed(range(0,W_P)): 
                       print 'previous_param:\n'  
                       print  previous_param   
                       print 'current_param:\n'  
                       print  current_param   
             
                       feature_list[W_P-1-w],labels = get_stats(line_count-w,input_dir,num_core,'OFFLINE',previous_param,current_param) 
                                            
                       if (w==0):#current features
                          old_labels=labels
                 try:#TODO for W_F > 1
                     feature_list_trash,labels = get_stats(line_count+(W_F),input_dir,num_core,'OFFLINE',previous_param,current_param) 
                     old_labels=labels 
                 except:
                     labels=old_labels
    
                 for core in range(num_core):
                     for w in range(0,W_P):                                                  
                         for f in feature_list[w]:                      
                                 Wfile_features_labels.write('%s,'%f[core])            
                     Wfile_features_labels.write('%s\n'%labels[core])
                     
                    #for w in (range(0,W_F-1)):
                 #    try:
                 #        feature_list_trash,labels = get_stats(line_count+(w+1),input_dir,num_core,'OFFLINE',line_splitted)
                 #        Wfile_features_labels.write('%s,'%labels[core])
                 #        old_labels=labels
                 #    except:
                 #        Wfile_features_labels.write('%s,'%old_labels[core]) 

                     #this version just works for W_F=1

                     #try:
                     #    feature_list_trash,labels = get_stats(line_count+(W_F),input_dir,num_core,'OFFLINE',line_splitted)
                     #    Wfile_features_labels.write('%s\n'%labels[core]) 
                     #except:
                     #    Wfile_features_labels.write('%s\n'%old_labels[core])                   


    Rfile_read_freq.close()  
    Wfile_features_labels.close()


