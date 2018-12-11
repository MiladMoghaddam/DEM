# DEM
The purpose of this work is to propose three novel techniques to optimize the energy of a network-on-chip based chip
multiprocessor under performance constraints.

Developed by:
   Milad Ghorbani Moghaddam, Dr. Cristinel Ababei
   milad.ghorbanimoghaddam@marquette.edu, cristinel.ababei@marquette.edu

This work is implemented with sniper simulator (V6.1).
Please download and install sniper and then add the attached directories to your workspace inside the ./sniper directory

---------------------------------------------------------------------------------------------------------------
   Kalman filtering based technique   
---------------------------------------------------------------------------------------------------------------
For more information please take a look at the following paper:
(Please cite it if you use it in your work)

  - M.G. Moghaddam and C. Ababei, “Dynamic energy management for chip multiprocessors under performance constraints,”
    Microprocessors and Microsystems, vol. 54, pp. 1-13, Oct. 2017.

---------------------------------------------------------------------------------------------------------------
Steps:


1) Run the benchmarks with Kalman filtering based technique to find the core frequencies based on the predicted 
   workload, To do so we can simply run the following sample command inside the benchmark folder:

   ./run-sniper -n 16 -c gainestown -c noc --roi -d ./kalman/barnes -sDVFS_PF_v2_pl10:1000000:0 -senergystats:1000000 \ 
    -g --perf_model/core/frequency=2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2 -p splash2-barnes -i small-16 -n 16

   The "DVFS_PF_v2_pl10" script (placed in ./sniper/scripts) is the main engine and optimizes the power by choosing 
   the best Voltage/Frequency pairs. In addition, this script as well as "energystats" script are modified in a way
   to extract many other statistics that can be used for different purposes.
   "DVFS_PF_v2_pl10" here is set to do the DVFS with 10% performance loss toleration. You can set other performance
   loss tolerations by modifying the file simply (there are also some samples for 5,10,20,30,40,50 percent 
   performance loss tolerations in the ./sniper/scripts folder)

   Note: The Kalman source code was downloaded from https://github.com/hmartiro/ and modified for our purpose.
         Check ./sniper/kalman for installation instruction.
---------------------------------------------------------------------------------------------------------------
   DNN based technique         
---------------------------------------------------------------------------------------------------------------
For more information please take a look at the following paper:
(Please cite it if you use it in your work)

  - M.G Moghaddam, W. Guan and C. Ababei, “Dynamic energy minimization in chip multiprocessors using deep neural 
    networks,” IEEE Trans. on Multiscale Computing Systems, 2018.

---------------------------------------------------------------------------------------------------------------
Steps:


1) Run the benchmarks with Kalman filtering based technique to find the core frequencies based on the predicted workload,
   collect runtime statistics and correct the frequencies based on the actual measured workload.
   To do so we can simply run the following sample command inside the benchmark folder:

   ./run-sniper -n 16 -c gainestown -c noc --roi -d ./kalman_corrected/barnes -sDVFS_PF_v2_pl10_corrected:1000000:0 \
   -senergystats:1000000  -g --perf_model/core frequency=2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2 -p splash2-barnes -i small-16 -n 16

   The "DVFS_PF_v2_pl10_corrected" script (placed in ./sniper/scripts) does everything for you and stores the frequencies
   in "Frequencies.xls". In addition, this script as well as    "energystats" script are modified in a way to extract many
    other statistics that can be used for different purposes.
   "DVFS_PF_v2_pl10_corrected" here is set to do the DVFS with 10% performance loss toleration. You can set other 
   performance loss tolerations by modifying the file simply (there are also some samples for 5,10,20,30,40,50 percent 
   performance loss tolerations in the ./sniper/scripts folder)


2) Collect the training data for the executed benchmarks ran by the kalman filtering technique.
   a- Make sure to have the tensorflow installed on your system
   b- Set the name of the trained model and data_set filename and DNN configuration in $sniper/script/user_level.py
      - Datasets are stored in ./sniper/DNN/data_sets
      - Trained models are stored in ./sniper/DNN/trained_model
   c- Collect the training data
      a- Copy "DNN_offline_bash.sh" and "DNN_offline_data_collector.py" from $sniper/scripts 
         to the directory contains the benchmark results
      b- Run "DNN_offline_bash.sh", it automatically collect the training data and stores it in the data_sets folder.


3) Train the data    
   a- Go to $sniper/scripts and run:
      python DNN_train.py 
      It automatically learns the features and stores the trained model in the Trained_model folder.
  
 
4) Running DNN based DVFS technique on sniper
   a- cd $sniper/benchmarks/
   b- Use the "DNN_predict_VF.py" and "energystats.py" scripts in ./sniper/scripts.
   c- Sample command:
      ./run-sniper -n 16 -c gainestown -c noc --roi -d ./DNN_run/barnes -sDNN_predict_VF:1000000:0 \
       -senergystats:1000000  -g --perf_model/core/frequency=2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2 \
       -p splash2-barnes -i small-16 -n 16


---------------------------------------------------------------------------------------------------------------
   LSTM based technique      
---------------------------------------------------------------------------------------------------------------
For more information please take a look at the following paper:
(Please cite it if you use it in your work)

  -  M.G Moghaddam, W. Guan and C. Ababei, “Investigation of LSTM based prediction for dynamic energy management 
     in chip multiprocessors,” IEEE Int. Conference on Green and Sustainable Computing (IGSC), 2017.

---------------------------------------------------------------------------------------------------------------
Steps:

1) Collect the training data for the executed benchmarks (this phase has some similarities with the DNN technique)
   a- Make sure to have the Keras installed on your system
   b- Set the name of the trained model and data_set filename and DNN configuration in $sniper/script/user_level.py
      - Datasets are stored in ./sniper/LSTM/data_sets
      - Trained models are stored in ./sniper/LSTM/trained_model
   c- Collect the training data
      a- Copy "DNN_offline_bash.sh" and "DNN_offline_data_collector.py" from $sniper/scripts 
         to the directory contains the benchmark results
      b- Run "DNN_offline_bash.sh", it automatically collect the training data and stores it in the data_sets folder.

2) go to ./sniper/scripts/ 
3) Modify LSTM_user_level.py script to set the dataset name and the column to be trained based on.
   Each column holds a statistic value (such as CPI or Instruction number) during the time.
4) To generate the trained_model and store it in .../sniper/LSTM/trained_model, run python LSTM_train.py
5) Sample run command:
      ./run-sniper -n 16 -c gainestown -c noc --roi -d ./LSTM_run/barnes -sLSTM_DVFS_pl10:1000000:0 \
       -senergystats:1000000  -g --perf_model/core/frequency=2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2 \
       -p splash2-barnes -i small-16 -n 16
 
---------------------------------------------------------------------------------------------------------------
#Note: in all the implementations you need to use the modified gen_simout.py and copy it in ./sniper/tools
Please find it in ./sniper/scripts
#Note: Please extract "libcarbon_sim.a.zip" inside the ./sniper/lib, before doing anything. I had to make compress
it due to filze size limitation in github
