import os
#import DNN_train_test as DNNTRAIN

sniper_path = "/home/milad/sniper"
###############################################################
###################### CONTROL PANEL ##########################
###############################################################
    
num_classes = 11  #based on the frequencies
layers = [500, 500, 500, 500, 300, 300, 400, 400]
#layers = DNNTRAIN.set_layers()
n_layers = len(layers)
dropout = 0.0

 #a sequence of features in the past
window_future = 1 #hard coded inside the code #a sequence of labels in future
######################
window_past = 5
n_core = 64
PL= 10
steps = 2000
optimizer = "Adagrad"
benchmark = "corrected_all"
version = 1
######################
slayers=''
for i in range(len(layers)):
  slayers+="_%s"%layers[i]

#trained_model_filename = "W%s_C%s_PL%s_S%s_%s_NL%s_%s_%s"%(window_past,n_core,PL,steps,optimizer,n_layers,benchmark,slayers)
#data_set_filename = "W%sC%sPL%s_%s"%(window_past,n_core,PL,benchmark) 


data_set_filename = "64_10-all"
#trained_model_filename = "test_%s"%data_set_filename
trained_model_filename = "W%s_C%s_PL%s_S%s_%s_NL%s_%s_%s"%(window_past,n_core,PL,steps,optimizer,n_layers,benchmark,slayers)

##############################################################
##############################################################
def get_sniper_path():
    return sniper_path
##############################################################
def get_trained_model_path():
    if not os.path.exists("%s/DNN/trained_model"%get_sniper_path()):
    	os.makedirs("%s/DNN/trained_model"%get_sniper_path(), 0777)
    model =  trained_model_filename
    return "%s/DNN/trained_model/%s"%(get_sniper_path(),model )
##############################################################
def get_trained_model_dir():
    if not os.path.exists("%s/DNN/trained_model"%get_sniper_path()):
    	os.makedirs("%s/DNN/trained_model"%get_sniper_path(), 0777)
    return "%s/DNN/trained_model"%(get_sniper_path() )
##############################################################
def get_data_set_dir():
    if not os.path.exists("%s/DNN/data_sets"%get_sniper_path()):
    	os.makedirs("%s/DNN/data_sets"%get_sniper_path(), 0777)
    return "%s/DNN/data_sets"%get_sniper_path()

##############################################################
def get_data_set_filename():    
    return "%s.csv"%data_set_filename
##############################################################
def get_data_set_file_path():    
    return "%s/DNN/data_sets/%s.csv"%(get_sniper_path(),data_set_filename)
##############################################################
def get_data_set_path():    
    return "%s/DNN/data_sets/"%get_sniper_path()

##############################################################
def get_num_classes():
    return num_classes
#############################################################
def get_layers():
    return layers
#############################################################
def get_slayers():
    return slayers
#############################################################
def get_dropout():
    return dropout
#############################################################
def get_optimizer():
    return optimizer
#############################################################
def get_num_steps():
    return steps
#############################################################
def get_window_past():
    return window_past
#############################################################
def get_window_future():
    return window_future
#############################################################

#For the freqs in DNN_predict.py
#FreqList=['1000','1100','1200','1300','1400','1500','1600','1700','1800','1900','2000']
#note: they should match those in DNN_predict_VF.py
def translate_class_to_freq(p):
  if (p==0):
     return 1000   
  elif (p==1):
     return 1100 
  elif (p==2):
     return 1200 
  elif (p==3):
     return 1300 
  elif (p==4):
     return 1400 
  elif (p==5):
     return 1500 
  elif (p==6):
     return 1600 
  elif (p==7):
     return 1700 
  elif (p==8):
     return 1800 
  elif (p==9):
     return 1900 
  elif (p==10):
     return 2000
  else:
     print '**** Wrong Class ****\n'
     return 2000 #default 


######################################################
def translate_freq_to_class(f):
  if (f==1000):
     return 0
  elif (f==1100):
     return 1   
  elif (f==1200):
     return 2 
  elif (f==1300):
     return 3 
  elif (f==1400):
     return 4 
  elif (f==1500):
     return 5 
  elif (f==1600):
     return 6 
  elif (f==1700):
     return 7 
  elif (f==1800):
     return 8 
  elif (f==1900):
     return 9 
  elif (f==2000):
     return 10 
  else:
     print '**** Wrong Frequency ****\n'
     return 10 #default 
#
#def translate_freq_to_class(f):
#  return float(f) #default 

