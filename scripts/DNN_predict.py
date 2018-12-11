import argparse
import sys

import numpy as np
import tensorflow as tf
import user_level as UL

features=[]
features_splitted=[]

tf.logging.set_verbosity(tf.logging.INFO)
print ("DNN_predict is running ...\n")

arg_feature_str=sys.argv[1]
prediction_file = sys.argv[2]
wfile=file(prediction_file,'w')

with open(arg_feature_str, 'r') as f:
    feature_str = f.readline()
#print "\n\n\n"
#print feature_str
#print "\n\n\n"
#######################################################################################################
def predict(features):
  feature_columns = [tf.contrib.layers.real_valued_column("", dimension=63)]
  my_nn = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                       hidden_units=UL.get_layers(),
                                       activation_fn=tf.nn.relu,
                                       dropout=UL.get_dropout,
                                       n_classes=UL.get_num_classes(),
                                       optimizer=UL.get_optimizer(),model_dir=UL.get_trained_model_path())

  feature_array = np.array(features,dtype=np.float32)  
  predictions = my_nn.predict(x=feature_array, as_iterable=True) #mode:INFER   -  no target should be set
  for i, p in enumerate(predictions):
    print("Prediction %s: %s" % (i + 1, p))
    #wfile.write("Prediction %s: %s" % (i + 1, p))
    freq=UL.translate_class_to_freq(p)
    wfile.write('%s\n'%freq)
#######################################################################################################

print ('feature_str= %s\n'%feature_str)
feature_array = feature_str.split('*')
print ('feature_array= %s\n'%feature_array)
len_feature_array = len(feature_array)-1 #last one is trash
print ("num arrays = %s"%len_feature_array)
for i in range(len_feature_array): 
    features.append([])
    features_splitted.append(feature_array[i].split(','))
    print ('features_splitted[%s]= %s\n'%(i,features_splitted[i]))

for i in range(len_feature_array): 
   for j in range (len(features_splitted[i])):
       features[i].append(float(features_splitted[i][j]))
print features

predict (features)

wfile.close()

