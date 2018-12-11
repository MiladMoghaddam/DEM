for f in 5 10 20 30 40 50
do	 
for f1 in 16_$f 64_$f #16_5,16_10 ...
do
      echo "training $f1-all"; 
      python DNN_train.py $f1-all.csv; 
done
done


