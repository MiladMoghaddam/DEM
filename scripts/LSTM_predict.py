import sys
import numpy
from keras.models import load_model
import LSTM_user_level as UL

input_file=sys.argv[1]
output_file=sys.argv[2]
ncore=int(sys.argv[3])
trained_model_name=sys.argv[4]

#input_file='./cpu_busy_time.xls'
#output_file='./LSTM_cpu_busy_time.txt'
#ncore=16

window_size= UL.get_window_past()
print input_file  
print output_file
print window_size
print ncore

features=[]
predictions=[]
for core in range(ncore):
    features.append([]) 
    predictions.append(0.0)

for core in range(ncore):
    for i in range(window_size): 
        features[core].append(0.0)


R_FILE = file(input_file, 'r')
total_line_count=-1
for line in R_FILE:
      total_line_count+=1        
print total_line_count

R_FILE = file(input_file, 'r')
line_count=-1
if (total_line_count-window_size>=0):
    for line in R_FILE:
        line_splitted = line.split('\t')
        line_count+=1 
        print "line_count=%s\n"%line_count
        if (line_count>=1) and (line_count<=total_line_count):
           if (line_count-(total_line_count-window_size)-1>=0):
                  for core in range(ncore):
                      print "line_count= %s ,X [%s][%s] = %s"%(line_count,core,line_count-(total_line_count-window_size)-1,float(line_splitted[core+2]) )
    	              features[core][line_count-(total_line_count-window_size)-1]=float(line_splitted[core+2]) 

else:
    print "else"
    for line in R_FILE:
        line_splitted = line.split('\t')
        line_count+=1 
        print "line_count=%s\n"%line_count
        
        if (line_count>=1):
           ''' # this part is to insert first element as the previous unknown elements
           if (line_count==1):
               for core in range(ncore):
                   for i in range(window_size): 
                       print ("first element=%s"%float(line_splitted[core+2]))
                       features[core][i]=float(line_splitted[core+2]) #filling all with the first element           
           else:           
           '''
           for core in range(ncore):                           
                   features[core][window_size-total_line_count+line_count-1]=float(line_splitted[core+2])


for i in range(window_size): 
        print ("%s\t"%features[0][i])

print ("%s\t"%features[0][i])


#model = load_model(UL.get_trained_model_path())
model = load_model("%s/LSTM/trained_model/%s"%(UL.get_sniper_path(),trained_model_name))
#NextFeature = numpy.array([[0.2,0.3,0.4,0.5,0.6]]) 
for core in range(ncore):
   NextFeature = numpy.array(features[core]) 
   NextFeature=NextFeature.reshape(1,1,window_size)
   NextPredict=model.predict(NextFeature)
   NextPredict=NextPredict.reshape(1)
   predictions[core]=NextPredict.tolist()[0]

print predictions

W_FILE=file(output_file,'w') 
for core in range(ncore-1):
    W_FILE.write("%s,"%predictions[core])
W_FILE.write("%s"%predictions[ncore-1])  
W_FILE.close()



