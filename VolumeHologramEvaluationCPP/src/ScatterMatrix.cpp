#include "ScatterMatrix.h"

namespace rcwa
{

 ScatterMatrix::ScatterMatrix(){}

 ScatterMatrix ScatterMatrix::Unity(int dimSij) {
     ScatterMatrix s;
     s.s11 = arma::cx_mat(dimSij, dimSij, arma::fill::zeros);
     s.s21 = arma::eye<arma::cx_mat>(dimSij, dimSij);
     s.s12 = arma::eye<arma::cx_mat>(dimSij, dimSij);
     s.s22 = arma::cx_mat(dimSij, dimSij, arma::fill::zeros);
     return s;
 }

 ScatterMatrix ScatterMatrix::redhefferStarProduct(const ScatterMatrix& sa, const ScatterMatrix& sb) {
     int dim = sa.s11.n_rows;
     arma::cx_mat i = arma::eye<arma::cx_mat>(dim, dim);
     ScatterMatrix sab;
     
     arma::cx_mat bracket_1 = arma::inv(i - (sb.s11 * sa.s22));
     arma::cx_mat bracket_2 = arma::inv(i - (sa.s22 * sb.s11));

     
     //SAB11
     arma::cx_mat second = sa.s12 * bracket_1 * (sb.s11 * sa.s21);
     sab.s11 = sa.s11 + second;

     //SAB12
     sab.s12 = sa.s12 * bracket_1 * sb.s12;

     //SAB21
     sab.s21 = sb.s21 * bracket_2 * sa.s21;

     //SAB22
     second = sb.s21 * bracket_2 * (sa.s22 * sb.s12);
     sab.s22 = sb.s22 + second;
     
     return sab;
 }

 void  ScatterMatrix::print(const std::string& msg) const {
     
     std::cout << msg <<  std::endl;
     
     (s11).raw_print("s11");
     (s21).raw_print("s21");
     (s12).raw_print("s12");
     (s22).raw_print("s22");
 }

}