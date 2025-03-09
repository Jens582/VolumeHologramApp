#include "EigenValuesVectors.h"
#include "SystemParameters.h"
#include "LayerData.h"
#include <armadillo>
#include <stdexcept>
#include<iostream>


namespace rcwa {
    EigenValuesVectors::EigenValuesVectors(const SystemParameters& system, const LayerData& layerData):mSystem(system){
        mBuildMe(layerData);
    }

    const arma::cx_mat& EigenValuesVectors::getV() const{
        return mV;
    }

    const arma::cx_mat& EigenValuesVectors::getW() const {
        return mW;
    }

    const arma::cx_mat& EigenValuesVectors::getLam() const {
        return mLam;
    }

    const arma::cx_mat& EigenValuesVectors::getArg() const {
        return mArg;
    }


    //Private 
    void EigenValuesVectors::mBuildMe(const LayerData& layerData) {
        mLi = layerData.li;
        mBuildConvolutionMatrices(layerData);
        mBuildQPOmega2();
        mBuildVWLam();
    }

    void EigenValuesVectors::mBuildConvolutionMatrices(const LayerData& layerData) {
        mErc = mBuildConvolutionMatrixFromErUr(layerData.er);
        mUrc = mBuildConvolutionMatrixFromErUr(layerData.ur);
    }
    arma::cx_mat EigenValuesVectors::mBuildConvolutionMatrixFromErUr(const arma::cx_mat& eRuR) {
        int total = mSystem.pGrid.n_elem;
        if (eRuR.n_rows == 1 && eRuR.n_cols == 1)
        {
            return arma::eye<arma::cx_mat>(total,total)*eRuR(0,0);
        }
        int dim = eRuR.n_rows * eRuR.n_cols;
        arma::cx_mat fft = arma::fft2(eRuR)/dim;
        arma::cx_mat spec = mFftShift2(fft);
             
        arma::ivec ps = arma::vectorise(mSystem.pGrid.t());
        arma::ivec qs = arma::vectorise(mSystem.qGrid.t());
        
        arma::cx_mat convolutionMatrix(total, total, arma::fill::zeros);
        
        for (int i = 0; i < total; i++) {
            int p = ps[i];
            int q = qs[i];
            arma::cx_rowvec vec = mGetRowFromSpectrumForConvolution(spec, p, q);
            convolutionMatrix.row(i) = vec;
        }
        return convolutionMatrix;
    }

    void EigenValuesVectors::mBuildQPOmega2() {

        arma::cx_mat ercInv = arma::inv(mErc);
        arma::cx_mat urcInv = arma::inv(mUrc);

        arma::cx_mat q00 = mSystem.kxNorm * urcInv * mSystem.kyNorm;
        arma::cx_mat q01 = mErc - (mSystem.kxNorm * urcInv * mSystem.kxNorm);
        arma::cx_mat q10 = (mSystem.kyNorm * urcInv * mSystem.kyNorm) - mErc;
        arma::cx_mat q11 = -mSystem.kyNorm * urcInv * mSystem.kxNorm;

        arma::cx_mat p00 = mSystem.kxNorm * ercInv * mSystem.kyNorm;
        arma::cx_mat p01 = mUrc - (mSystem.kxNorm * ercInv * mSystem.kxNorm);
        arma::cx_mat p10 = (mSystem.kyNorm * ercInv * mSystem.kyNorm) - mUrc;
        arma::cx_mat p11 = -mSystem.kyNorm * ercInv * mSystem.kxNorm;

        mQ = mCombineMatrix(q00, q01, q10, q11);
        mP = mCombineMatrix(p00, p01, p10, p11);
        mOmega2 = mP * mQ;
        
    }

    void EigenValuesVectors::mBuildVWLam() {        
        double accu = arma::accu(arma::abs(mOmega2)) - arma::accu(arma::abs(mOmega2.diag()));
        bool isDiagonal = (accu<1e-9) ;        
        int dim = mOmega2.n_rows;
        
        arma::cx_vec diagonal;
                
        if (isDiagonal) {
                        
            mCheckForKzZero(mOmega2);
            diagonal = mOmega2.diag();            
            mW = arma::eye<arma::cx_mat>(dim, dim);
        }
        else {
            bool success = arma::eig_gen(diagonal, mW, mOmega2);            
            if (!success) {
                throw std::runtime_error("Could not calculate eigenvalues");
            }
         }
        
        
        arma::cx_mat lam2 = arma::cx_mat(dim, dim, arma::fill::zeros);        
        lam2.diag() = diagonal;                
        mLam = mSignConventionSqrt(lam2);
      
        arma::cx_mat lamInv = arma::inv(mLam);
        mV = mQ * mW * lamInv;
        double k0 = mSystem.param.k0;        
        mArg = -mLam * k0 * mLi;
        
    }

    arma::cx_mat EigenValuesVectors::mSignConventionSqrt(const arma::cx_mat& a) {
        arma::cx_mat sqrt = arma::sqrt(a);
        arma::mat s = arma::sign(arma::imag(sqrt));
        arma::mat mul = 1 + s * (1 - s);
        return -mul % sqrt;
    }

    void EigenValuesVectors::mCheckForKzZero(const arma::cx_mat& omega2){
        arma::vec diag_abs = arma::abs(omega2.diag()); 
        bool check =  arma::all(diag_abs < 1e-8);
        if (check) {
            throw std::runtime_error("KZ is zero, Change incident angle or grating");
        }
    }
    
    arma::cx_mat EigenValuesVectors::mCombineMatrix(const arma::cx_mat& a00, const arma::cx_mat& a01, const arma::cx_mat& a10, const arma::cx_mat& a11) {
                
        arma::cx_mat top = arma::join_rows(a00, a01);
        arma::cx_mat bottom = arma::join_rows(a10, a11);
        return  arma::join_cols(top, bottom);
        
    }

    arma::cx_mat EigenValuesVectors::mFftShift2(const arma::cx_mat& eRuR) {
        int shift0 = (eRuR.n_rows - 1) / 2;
        int shift1 = (eRuR.n_cols - 1) / 2;
        arma::cx_mat shift = arma::shift(eRuR, shift0, 0);
        return arma::shift(shift, shift1, 1);
    }

    arma::cx_rowvec EigenValuesVectors::mGetRowFromSpectrumForConvolution(const arma::cx_mat& spec, int p, int q) {
        int my = (spec.n_rows - 1) / 2;
        int mx = (spec.n_cols - 1) / 2;
        int sy = (my + q - mSystem.param.harmonicOrderY);
        int sx = (mx + p - mSystem.param.harmonicOrderX);
        int ey = (my + q + mSystem.param.harmonicOrderY); // armadillo: without +1 as numpy 
        int ex = (mx + p + mSystem.param.harmonicOrderX);
        arma::cx_mat sub = spec.submat(sy, sx, ey, ex);
        arma::cx_rowvec vec = arma::vectorise(sub.t()).t(); // Transpose like in Numpy
        return arma::reverse(vec);
    }
}
