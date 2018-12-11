#python DNN_train_pass_layers.py layers
#it takes the data set and the model name and path from user_level_pass_layers

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import tempfile
import os

# Import urllib
from six.moves import urllib

import numpy as np
import tensorflow as tf
from tensorflow.contrib.learn.python.learn.estimators import model_fn as model_fn_lib

import user_level_pass_layers as UL

FLAGS = None

tf.logging.set_verbosity(tf.logging.INFO)

print (sys.argv[1])

slayers = sys.argv[1]
layers = slayers.split(',')
for l in range(len(layers)):
    layers[l] = int(layers[l])

print (layers)


def set_layers():
    return layers

def evaluate_predict (file_name,nn):
  WFILE_report = open("%s/report.txt"%UL.get_trained_model_dir(),"a")
  WFILE_report.write("\n\n**********************************************************\n") 
  WFILE_report.write("**********************************************************\n")
  WFILE_report.write("trained_model:\n%s\n"%UL.get_trained_model_path())
  WFILE_report.write("**********************************************************\n")
  WFILE_report.write("**********************************************************\n")
  WFILE_report.write("layes: %s\n"%UL.get_layers())
  WFILE_report.write("optimizer: %s\n"%UL.get_optimizer())
  WFILE_report.write("steps: %s\n"%UL.get_num_steps())
  WFILE_report.write("dropout: %s\n"%UL.get_dropout())
  WFILE_report.write("num_classes: %s\n"%UL.get_num_classes())
  WFILE_report.write("**********************************************************\n")
  WFILE_report.write("evaluation_set: %s.csv\n"%file_name)
  WFILE_report.write("**********************************************************\n")  

  print ("\n*****%s*****\n"%file_name)
  data_set = tf.contrib.learn.datasets.base.load_csv_without_header(
      filename="%s%s.csv"%(UL.get_data_set_path(),file_name), target_dtype=np.int, features_dtype=np.float32,target_column=-1)
  # Evaluate accuracy.
  accuracy_score = nn.evaluate(x=data_set.data,
                                    y=data_set.target)
  print('accuracy: ',accuracy_score["accuracy"])
  print('loss: ',accuracy_score["loss"])
  #print('auc: ',accuracy_score["auc"])
  print('global_step: ',accuracy_score["global_step"])
  #print('Accuracy: {0:f}'.format(accuracy_score))
  print ("DONE with DNN_train.py")
  WFILE_report.write('accuracy: %s\n'%accuracy_score["accuracy"])
  WFILE_report.write('loss: %s\n'%accuracy_score["loss"])
  WFILE_report.write('global_step: %s\n'%accuracy_score["global_step"])

  ###########################################################################
  predictions = nn.predict(x=data_set.data, as_iterable=True) 
  print ("\n%s:\n"%file_name)
  print ("\nDNN Training:\n")
  WFILE_report.write("\nDNN Training:\n")
  count= []
  for k in range (0,11):
      count.append(0)
  for i in data_set.target:
      for k in range (0,11):
          if (i==k):
              count[k]+=1
  for k in range (0,11):
      print ("count[%s] (freq: %s) = %s"%(k,UL.translate_class_to_freq(k),count[k]))
      WFILE_report.write("count[%s] (freq: %s) = %s\n"%(k,UL.translate_class_to_freq(k),count[k]))

  print ("\nDNN Prediction:\n")
  WFILE_report.write("\nDNN Prediction:\n")
  predict_count= []
  total_count=0
  for k in range (0,11):
      predict_count.append(0)
  for i, p in enumerate(predictions):    

      total_count+=1
      for k in range (0,11):
          if (p==k):
              predict_count[k]+=1
  for k in range (0,11):
      print ("predict_count[%s] (freq: %s) = %s"%(k,UL.translate_class_to_freq(k),predict_count[k]))
      WFILE_report.write("predict_count[%s] (freq: %s) = %s\n"%(k,UL.translate_class_to_freq(k),predict_count[k]))
  print ("Total= %s"%total_count)
  WFILE_report.write("Total= %s\n"%total_count)
  WFILE_report.close()


def remove_csv(filename):
    string=filename.split('.')
    return (string[0])
def evaluate_test_cases(filename,nn):
    '''
    string=filename.split('_')
    #evaluate_predict(filename,nn)
    evaluate_predict("%s_corrected_parsec"%string[0],nn) 
    evaluate_predict("%s_corrected_splash"%string[0],nn) 
    evaluate_predict("%s_corrected_all"%string[0],nn)
    '''
    string=filename.split('-')
    #evaluate_predict(filename,nn)
    evaluate_predict("%s-all"%string[0],nn) 
    evaluate_predict("%s-parsec"%string[0],nn) 
    evaluate_predict("%s-splash2"%string[0],nn)

    #evaluate_predict("%s_parsec"%string[0],nn)
    #evaluate_predict("%s_splash"%string[0],nn) 
    #evaluate_predict("%s_ALL"%string[0],nn)  
    #evaluate_predict("%s_ALLpls"%string[0],nn) 
##################################
##################################
##################################

def main(unused_argv):
  # Load datasets
  #abalone_train, abalone_test, abalone_predict = maybe_download(
  #  FLAGS.train_data, FLAGS.test_data, FLAGS.predict_data)

  if os.path.exists(UL.get_trained_model_path()):
     os.system("rm -r %s"%UL.get_trained_model_path())

  train_file_name= UL.get_data_set_file_path()
  test_file_name= UL.get_data_set_file_path()  
  
  # Training examples
  training_set = tf.contrib.learn.datasets.base.load_csv_without_header(
      filename=train_file_name, target_dtype=np.int, features_dtype=np.float32,target_column=-1)

  # Test examples
  test_set = tf.contrib.learn.datasets.base.load_csv_without_header(
      filename=test_file_name, target_dtype=np.int, features_dtype=np.float32,target_column=-1)

  # Test examples1
  #prediction_set = tf.contrib.learn.datasets.base.load_csv_without_header(
  #    filename=test_file_name, target_dtype=np.int, features_dtype=np.float32,target_column=-1)


  #############################

  feature_columns = [tf.contrib.layers.real_valued_column("", dimension=8)]
  '''
  #validation_monitor = tf.contrib.learn.monitors.ValidationMonitor(test_set.data,
  #                                                                 test_set.target,
  #                                                                 every_n_steps=50)
  #my_nn = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
  #                                     hidden_units=[20],
  #                                     activation_fn=tf.nn.relu,
  #                                     dropout=0.2,n_classes=UL.get_num_classes(),                                     
  #                                     optimizer="Adam",model_dir=UL.get_trained_model_path(),
  #                                     config=tf.contrib.learn.RunConfig(save_checkpoints_secs=1))
  #my_nn.fit(x=training_set.data,y=training_set.target,steps=1000,monitors=[validation_monitor])
  '''
  my_nn = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                       hidden_units=UL.get_layers(),
                                       activation_fn=tf.nn.relu,
                                      dropout=UL.get_dropout(),n_classes=UL.get_num_classes(),                                     
                                       optimizer=UL.get_optimizer(),model_dir=UL.get_trained_model_path())


    

  my_nn.fit(x=training_set.data,y=training_set.target,steps=UL.get_num_steps())

  
  evaluate_test_cases(remove_csv(UL.get_data_set_filename()),my_nn)
  #evaluate_predict(remove_csv(UL.get_data_set_filename()),my_nn)
  #evaluate_predict("W10C16PL5_splash",my_nn)

####################################
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.register("type", "bool", lambda v: v.lower() == "true")
  parser.add_argument(
      "--train_data", type=str, default="", help="Path to the training data.")
  parser.add_argument(
      "--test_data", type=str, default="", help="Path to the test data.")
  parser.add_argument(
      "--predict_data",
      type=str,
      default="",
      help="Path to the prediction data.")
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
####################################


