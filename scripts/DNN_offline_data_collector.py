import sys,os
sys.path.insert(0, '/home/milad/sniper/scripts/')
import DNN_feature_collector as DFC
import user_level as UL 

input_filename= 'Frequencies.xls'

output_filename = UL.get_data_set_filename()

input_dir = sys.argv[1]

output_dir= UL.get_data_set_dir()

CMP_based_DNN_flag = 0

DFC.collect_offline_window_based(input_dir,input_filename,output_dir,output_filename,'CORE_BASED')


