/**
* Implementation of KalmanFilter class.
*
* @author: Hayk Martirosyan
* @date: 2014.11.15
*/

#include <iostream>
#include <stdexcept>

#include "kalman.hpp"

KalmanFilter::KalmanFilter(
    double dt,
    const Eigen::MatrixXd& A,
    const Eigen::MatrixXd& C,
    const Eigen::MatrixXd& Q,
    const Eigen::MatrixXd& R,
    const Eigen::MatrixXd& P)
  : A(A), C(C), Q(Q), R(R), P0(P),
    m(C.rows()), n(A.rows()), dt(dt), initialized(false),
    I(n, n), x_hat(n), x_hat_new(n), x_predicted(n)
{
  I.setIdentity();
}

KalmanFilter::KalmanFilter() {}

void KalmanFilter::init(double t0, const Eigen::VectorXd& x0) {
  x_hat = x0;
  P = P0;
  this->t0 = t0;
  t = t0;
  initialized = true;
}

void KalmanFilter::init() {
  x_hat.setZero();
  P = P0;
  t0 = 0;
  t = t0;
  initialized = true;
}

void KalmanFilter::update(const Eigen::VectorXd& y) {

  if(!initialized)
    throw std::runtime_error("Filter is not initialized!");

  x_predicted = A * x_hat;
  P = A*P*A.transpose() + Q; // P = P+Q


  K = P*C.transpose()*(C*P*C.transpose() + R).inverse();// K = P/(P+R)
  x_hat_new += K * (y - C*x_predicted);// x_hat_new = x_hat_new + K(y-x_predicted)
  P = (I - K*C)*P;
  x_hat = x_hat_new;
  
  

  t += dt;
}




void KalmanFilter::update(const Eigen::VectorXd& y, double dt, const Eigen::MatrixXd A) {

  this->A = A;
  this->dt = dt;
  update(y);
}


void KalmanFilter::updateTimeVarying(const Eigen::VectorXd& y, const Eigen::MatrixXd An, const Eigen::MatrixXd Qn, const Eigen::MatrixXd Rn ) {
    A=An;
    Q=Qn;
    R=Rn;
    

  if(!initialized)
    throw std::runtime_error("Filter is not initialized!");

  x_predicted = A * x_hat;
  P = A*P*A.transpose() + Q; // P = P+Q


  K = P*C.transpose()*(C*P*C.transpose() + R).inverse();// K = P/(P+R)
  x_hat_new += K * (y - C*x_predicted);// x_hat_new = x_hat_new + K(y-x_predicted)
  P = (I - K*C)*P;
  x_hat = x_hat_new;
  

  

  t += dt;
}

void KalmanFilter::UpdatePredict_TimeVarying(const Eigen::VectorXd& y, const Eigen::VectorXd& x_predicted_old, const Eigen::MatrixXd An, const Eigen::MatrixXd Qn, const Eigen::MatrixXd Rn ) {
    A=An;
    Q=Qn;
    R=Rn;
    

  if(!initialized)
    throw std::runtime_error("Filter is not initialized!");
/*
  x_predicted = A * x_hat;
  P = A*P*A.transpose() + Q; // P = P+Q


  K = P*C.transpose()*(C*P*C.transpose() + R).inverse();// K = P/(P+R)
  x_hat_new += K * (y - C*x_predicted);// x_hat_new = x_hat_new + K(y-x_predicted)
  P = (I - K*C)*P;
  x_hat = x_hat_new;
*/  
  K = P*C.transpose()*(C*P*C.transpose() + R).inverse();// K = P/(P+R)
  x_hat_new += K * (y - C*x_predicted_old);// x_hat_new = x_hat_new + K(y-x_predicted)
  P = (I - K*C)*P;
  x_hat = x_hat_new;

  x_predicted = A * x_hat;
  P = A*P*A.transpose() + Q; // P = P+Q


  

  t += dt;
}
