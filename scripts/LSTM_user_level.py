import os
sniper_path = "/home/milad/sniper"
###############################################################
###################### CONTROL PANEL ##########################
###############################################################

######################
window_past = 20#


#column_to_train = 0#CoreIns
#column_to_train = 1#IPC
#column_to_train = 2#IdleTimePerc
column_to_train = 6#cpu_busy_time

#optimizer = "Adagrad"
######################
#trained_model_filename = "LSTM_W%s_C%s_PL%s_S%s_%s_NL%s_%s_%s"%(window_past,n_core,PL,steps,optimizer,n_layers,benchmark,slayers)
#data_set_filename = "LSTM_W%sC%sPL%s_%s"%(window_past,n_core,PL,benchmark) 

#trained_model_filename = "trained_CoreIns"
#trained_model_filename = "trained_IPC"
#trained_model_filename = "trained_IdleTimePerc"
trained_model_filename = "trained_cpu_busy_time"

data_set_filename = "16_5-all" #csv file

##############################################################
##############################################################
def get_sniper_path():
    return sniper_path
##############################################################
def get_trained_model_path():#
    if not os.path.exists("%s/LSTM/trained_model"%get_sniper_path()):
    	os.makedirs("%s/LSTM/trained_model"%get_sniper_path(), 0777)
    model =  trained_model_filename
    return "%s/LSTM/trained_model/%s"%(get_sniper_path(),model )
##############################################################
def get_trained_model_dir():
    if not os.path.exists("%s/LSTM/trained_model"%get_sniper_path()):
    	os.makedirs("%s/LSTM/trained_model"%get_sniper_path(), 0777)
    return "%s/LSTM/trained_model"%(get_sniper_path() )
##############################################################
def get_data_set_dir():
    if not os.path.exists("%s/LSTM/data_sets"%get_sniper_path()):
    	os.makedirs("%s/LSTM/data_sets"%get_sniper_path(), 0777)
    return "%s/LSTM/data_sets"%get_sniper_path()
##############################################################
def get_column_to_train():#
    return column_to_train
##############################################################
def get_data_set_filename():#    
    return "%s.csv"%data_set_filename
#############################################################
def get_window_past():#
    return window_past
##############################################################
def get_data_set_file_path():    
    return "%s/LSTM/data_sets/%s.csv"%(get_sniper_path(),data_set_filename)
##############################################################
def get_optimizer():
    return optimizer

