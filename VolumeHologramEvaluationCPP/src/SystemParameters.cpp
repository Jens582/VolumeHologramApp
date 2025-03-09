#include "SystemParameters.h"
#include "Parameter.h"
#include <numbers>
#include <armadillo>
#include <iostream>
#include <complex>

namespace rcwa {

	SystemParameters::SystemParameters(){}
	SystemParameters::SystemParameters(Parameter& param,
		arma::imat& pGrid, arma::imat& qGrid,
		arma::cx_mat& kxNorm, arma::cx_mat& kyNorm,
		arma::cx_mat& kzRefNorm, arma::cx_mat& kzTrnNorm,
		arma::cx_vec& cIncSPol, arma::cx_vec& cIncPPol,
		std::shared_ptr<const DeviceCreator> deviceCreator
	): param(param), pGrid(pGrid), qGrid(qGrid),
		kxNorm(kxNorm), kyNorm(kyNorm), kzRefNorm(kzRefNorm), kzTrnNorm(kzTrnNorm),
		cIncSPol(cIncSPol), cIncPPol(cIncPPol), deviceCreator(deviceCreator)
	{}


	SystemParameterCreator::SystemParameterCreator(const Parameter& pram): mParam(pram){}

	SystemParameters SystemParameterCreator::createSystemParameters(const Parameter& pram, std::shared_ptr<const DeviceCreator> deviceCreator) {
		SystemParameterCreator creator(pram);
		creator.mBuildMe();
		SystemParameters system(creator.mParam,
			creator.mPGrid, creator.mQGrid,
			creator.mKxNorm, creator.mKyNorm,
			creator.mKzRefNorm, creator.mKzTrnNorm,
			creator.mCIncSPol, creator.mCIncPPol,
			deviceCreator
		);
		return system;
	}

	void SystemParameterCreator::mBuildMe() {
		mBuildGrids();
		mBuildKxyNorm();
		mBuildKzRefTrn();
		mCalcSPol();
	}

	
	void SystemParameterCreator::mBuildGrids() {
		int x = mParam.harmonicOrderX;
		int y = mParam.harmonicOrderY;
		int nx = 2 * x + 1;
		int ny = 2 * y + 1;

		arma::ivec vx = arma::linspace<arma::ivec>(-x, x, nx);
		arma::ivec vy = arma::linspace<arma::ivec>(-y, y, ny);
				
		mPGrid = arma::repmat(vx.t(), ny, 1);
		mQGrid = arma::repmat(vy, 1, nx);

	}

	void SystemParameterCreator::mBuildKxyNorm() {
		arma::vec ps = arma::conv_to<arma::vec>::from(arma::vectorise(mPGrid.t()));
		arma::vec qs = arma::conv_to<arma::vec>::from(arma::vectorise(mQGrid.t()));
		
		arma::cx_vec kxDiag = (mParam.kxInc - ps * mParam.t1X - qs * mParam.t2X) / mParam.k0;
		arma::cx_vec kyDiag = (mParam.kyInc - ps * mParam.t1Y - qs * mParam.t2Y) / mParam.k0;
		
		int dim = kxDiag.n_elem;

		mKxNorm = arma::cx_mat(dim, dim);
		mKyNorm = arma::cx_mat(dim, dim);
		
		mKxNorm.diag() = kxDiag;
		mKyNorm.diag() = kyDiag;
		
	}
	
	void SystemParameterCreator::mBuildKzRefTrn() {
		std::complex<double> preFaktor;
		preFaktor = std::conj(mParam.erRef) * std::conj(mParam.urRef);
		mKzRefNorm = -mBuildKzNormSqrt(preFaktor);
		
		preFaktor = std::conj(mParam.erTrn) * std::conj(mParam.urTrn);
		mKzTrnNorm = mBuildKzNormSqrt(preFaktor);
	}

	void SystemParameterCreator::mCalcSPol() {		
		std::complex<double> kx = mParam.kxInc;
		std::complex<double> ky = mParam.kyInc;
		std::complex<double> kz = mParam.kzInc;
		arma::cx_vec3 k = { kx,ky,kz };
		arma::cx_vec3 ez(arma::fill::zeros);
		ez(2) = { 1.0,0.0 };
				
		bool isParallel = (abs(kx)+abs(ky))<1e-6;

		arma::cx_vec sPol;
		arma::cx_vec pPol;

		if(isParallel)
		{
			sPol = arma::cx_vec(3, arma::fill::zeros);
			pPol = arma::cx_vec(3, arma::fill::zeros);
			sPol(1) = {1.0,0.0};
			pPol(0) = {1.0,0.0};
		}
		else{
			sPol = arma::normalise(arma::cross(k, ez));
			pPol = arma::normalise(arma::cross(k, sPol));
		}

		int dim = mKxNorm.n_rows;
		
		mCIncSPol = arma::cx_vec(2*dim, arma::fill::zeros);
		mCIncPPol = arma::cx_vec(2*dim, arma::fill::zeros);

		int iX = int((dim - 1) / 2);
		int iY = iX+dim;

		mCIncSPol(iX) = sPol(0);
		mCIncSPol(iY) = sPol(1);

		mCIncPPol(iX) = pPol(0);
		mCIncPPol(iY) = pPol(1);

	}

	arma::cx_mat SystemParameterCreator::mBuildKzNormSqrt(std::complex<double> preFaktor) {
		int n_rows = mKxNorm.n_rows;
		int n_cols = mKxNorm.n_cols;

		arma::cx_mat I = arma::eye<arma::cx_mat>(n_rows, n_cols);
		arma::cx_mat square = preFaktor * I - (arma::square(mKxNorm) + arma::square(mKyNorm));
		arma::cx_mat sqrt = arma::sqrt(square);
		return arma::conj(sqrt);
	}

}