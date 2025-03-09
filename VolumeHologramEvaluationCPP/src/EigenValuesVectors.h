#pragma once
#include "SystemParameters.h"
#include "LayerData.h"
#include <armadillo>

namespace rcwa {

	class EigenValuesVectors{
	public:
		EigenValuesVectors(const SystemParameters& system, const LayerData& layerData);
        const arma::cx_mat& getV() const;
        const arma::cx_mat& getW() const;
        const arma::cx_mat& getLam() const;
        const arma::cx_mat& getArg() const;

    private:
        SystemParameters mSystem;
        double mLi;
        arma::cx_mat mErc{};
        arma::cx_mat mUrc{};

        arma::cx_mat mQ{};
        arma::cx_mat mP{};
        arma::cx_mat mOmega2{};

        arma::cx_mat mV{};
        arma::cx_mat mW{};
        arma::cx_mat mLam{};
        arma::cx_mat mArg{};
                

        void mBuildMe(const LayerData& layerData);
        void mBuildConvolutionMatrices(const LayerData& layerData);
        void mBuildQPOmega2();
        void mBuildVWLam();

        arma::cx_mat mBuildConvolutionMatrixFromErUr(const arma::cx_mat& eRuR);
        arma::cx_rowvec mGetRowFromSpectrumForConvolution(const arma::cx_mat& spec, int p, int q);
        static arma::cx_mat mFftShift2(const arma::cx_mat& eRuR);
        static arma::cx_mat mCombineMatrix(const arma::cx_mat& a00, const arma::cx_mat& a01, const  arma::cx_mat& a10, const arma::cx_mat& a11);
        void mCheckForKzZero(const  arma::cx_mat& omega2);
        static arma::cx_mat mSignConventionSqrt(const arma::cx_mat& a);
	};
}


