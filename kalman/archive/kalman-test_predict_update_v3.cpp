/**
 * Test for the KalmanFilter class with 1D projectile motion.
 *
 * @author: Hayk Martirosyan
 * @date: 2014.11.15
 */

#include <iostream>
#include <vector>
#include <Eigen/Dense>
#include <fstream>
#include <string>

#include "kalman.hpp"
using namespace std;

int main(int argc, char* argv[]) {
  cout << "Running Kalman Filter" <<endl;
  char *dirpath;
  char *infile_name;
  char *outfile_name;
   

  if (argc ==3){
	infile_name=argv[1];
    outfile_name=argv[2];
  }
  else
  {
	cout << "ERROR: kalman in-out file path not passed correctly" <<endl;
    exit(1);
  }
  cout << "infile: " << infile_name << endl;
  cout << "outfile: " << outfile_name << endl;
  int n = 1; // Number of states
  int m = 1; // Number of measurements
  
  double dt = 1.0/1; // Time step
  int num_cores;

  Eigen::MatrixXd A(n, n); // System dynamics matrix
  Eigen::MatrixXd C(m, n); // Output matrix
  Eigen::MatrixXd Q(n, n); // Process noise covariance
  Eigen::MatrixXd R(m, m); // Measurement noise covariance
  Eigen::MatrixXd P(n, n); // Estimate error covariance

  // Discrete LTI projectile motion, measuring position only
  A << 1;  
  C << 1;
  //A << 1, dt, 0, 0, 1, dt, 0, 0, 1;
	//C <<1;
  
  //C << 1, 0, 0;
  //A << 1, 0, 0, 0, 1, 0, 0, 0, 1;
  // Reasonable covariance matrices
  //Q << .05, .05, .0, .05, .05, .0, .0, .0, .0;
  //Q << .05, .05, .0, .05;
  Q << 0.5;
	//Q << .05, .0, .0, .0, .05, .0, .0, .0, .05;
  
  R << 0.1;
  P <<0.1;
  //P << .1, .1, .1, .1, 10000, 10, .1, 10, 100; 
  //P << .1, .1, .1, .1;
  

  std::cout << "A: \n" << A << std::endl;
  std::cout << "C: \n" << C << std::endl;
  std::cout << "Q: \n" << Q << std::endl;
  std::cout << "R: \n" << R << std::endl;
  std::cout << "P: \n" << P << std::endl;

  // Construct the filter
  KalmanFilter kf(dt, A, C, Q, R, P);
  cin.get();
  // List of noisy position measurements (y)
  
  
  double doubleTemp;

  std::vector<Eigen::MatrixXd> Qn;
  std::vector<Eigen::MatrixXd> Rn;
  std::vector<Eigen::MatrixXd> An; 
  std::vector<vector <double>> measurements_array;
  std::vector<vector <double>> predicted_array;
  std::vector<vector <double>> x_hat_new_array;
  std::vector<vector <double>> Error_array;
  std::vector<vector<Eigen::MatrixXd>> Qn_array;
  std::vector<vector<Eigen::MatrixXd>> Rn_array;
  std::vector<vector<Eigen::MatrixXd>> An_array;
  vector<KalmanFilter> kf_array;
  
  string line;

  ifstream infile (infile_name);
  ofstream outfile (outfile_name);
  double line_count;

  if (infile.is_open())
  {
    line_count=-1;
    while ( getline (infile,line) )
    {
	  line_count++;
      cout <<"l#"<<line_count<<": ";
      cout << line << '\n';
      istringstream stringline(line);
      int line_tab_count=-1;

      while (stringline)
      {         
        string data;
		if (!getline (stringline,data,'\t'))break;
            line_tab_count++;
			cout << "data="<<data<<"\n";
			cout << "line_tab_count="<<line_tab_count<<"\n";
            if (line_count == 0){
				if (line_tab_count == 0){
                    string::size_type sz;
					num_cores = stoi (data,&sz); //convert str to int
					cout <<"num_cores: "<<num_cores<<endl;
					cin.get();
					
                    for (int i=0;i<num_cores;i++){
                         vector <double> row_double;						 
						 vector<Eigen::MatrixXd> row_matrix;
						 measurements_array.push_back(row_double); 
						 predicted_array.push_back(row_double);
                         x_hat_new_array.push_back(row_double);
						 Error_array.push_back(row_double);
 						 Qn_array.push_back(row_matrix);
                         Rn_array.push_back(row_matrix);
						 An_array.push_back(row_matrix);                 
						 kf_array.push_back(kf); // based on the initial kf
						 
                    }
                }
			}
            else {
				for (int i=0;i<num_cores;i++)
              	    if (line_tab_count==i+2){
						doubleTemp = atof(data.c_str());
						measurements_array[i].push_back(doubleTemp);						
                }
			}
	  }

    }
    infile.close();
  }
  else
      cout <<"no file" << '\n';

  for (int i=0;i<num_cores;i++)
	for (int j=0;j<line_count;j++)
		cout <<"measurements["<<i<<"]["<<j<<"]: "<< measurements_array[i][j] <<endl;



  //////////////////////////////////////////////////////////////////////////////////////
  // Best guess of initial states

  for (int core=0;core<num_cores;core++){
  	Eigen::VectorXd x0(n);
  	//x0 << measurements[0], 0, 0;//-9.81  
	x0 << measurements_array[core][0];
    // initializing   
  	kf_array[core].init(0,x0);

    // Feed measurements into filter, output estimated states
    double t = 0;
    int prev_i=0;
    Eigen::VectorXd y(m);
    //std::cout << "t = " << t << ", " << "x_hat[0]: " << kf.state().transpose() << std::endl;


	  	  for(int i = 0; i < measurements_array[core].size(); i++){
    		  t += dt;
		      y << measurements_array[core][i];
    	      if (i==0) {
				prev_i=0;
			  	Qn.push_back(Q);
    	      	Rn.push_back(R);
    	      	An.push_back(A);
			  }
			  else {
    	      	prev_i=i-1;
			  	Qn.push_back(1*Qn[prev_i]);
    	      	Rn.push_back(1*Rn[prev_i]);
    	      	An.push_back(1*An[prev_i]);
			  }
			  kf_array[core].updateTimeVarying(y,An[i],Qn[i],Rn[i]);

    	      //kf.update(y);
		      std::cout << "t = " << t << ", " << "y[" << i << "] = " << y.transpose()
    	                << ", x_hat[" << i << "] = " << kf_array[core].state().transpose() << std::endl;              
			  predicted_array[core].push_back(kf_array[core].state().transpose()[0]);
              x_hat_new_array[core].push_back(kf_array[core].state_x_new().transpose()[0]);
			  Error_array[core].push_back((y.transpose()[0]-kf_array[core].state().transpose()[0])/y.transpose()[0]);
		 }
		  
  }//end [for core ...]


  if (outfile.is_open()){
     for (int core=0;core<num_cores;core++)
	 	outfile << "Core"<<'\t'<<"Interval" <<'\t' << "Measurments"<<'\t'<< "Predicted" << '\t' << "x_hat" << '\t' << '\t' << "Error %";
	  	for(int i = 0; i < measurements_array[0].size(); i++){ //line_count
		  outfile << endl;
    	  for (int core=0;core<num_cores;core++){    
			 outfile << core <<'\t' << i <<'\t' << measurements_array[core][i] <<'\t' << predicted_array[core][i] <<'\t' 
 	  		 << x_hat_new_array[core][i] <<'\t'<< Error_array[core][i] << '\t';
		  }
	}	
  outfile.close();
  }


  return 0;
}
