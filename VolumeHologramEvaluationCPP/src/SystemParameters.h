#pragma once
#include "Parameter.h"
#include "DeviceCreator.h"
#include <numbers>
#include <armadillo>
#include <complex>
#include <array>
#include <memory>

namespace rcwa {


	struct SystemParameters
	{			
		SystemParameters();
		SystemParameters(Parameter& param,
			arma::imat& pGrid, arma::imat& qGrid,
			arma::cx_mat& kxNorm, arma::cx_mat& kyNorm,
			arma::cx_mat& kzRefNorm, arma::cx_mat& kzTrnNorm,
			arma::cx_vec& cIncSPol, arma::cx_vec& cIncPPol,
			std::shared_ptr<const DeviceCreator> deviceCreator
			);

		const Parameter param;
		const arma::imat pGrid;
		const arma::imat qGrid;

		const arma::cx_mat kxNorm;
		const arma::cx_mat kyNorm;
		const arma::cx_mat kzRefNorm;
		const arma::cx_mat kzTrnNorm;

		const arma::cx_vec cIncSPol;
		const arma::cx_vec cIncPPol;

		const std::shared_ptr<const DeviceCreator> deviceCreator;

	};

	class SystemParameterCreator {
	public:
		SystemParameterCreator(const Parameter& pram);
		static SystemParameters createSystemParameters(const Parameter& pram, std::shared_ptr<const DeviceCreator> deviceCreator);
	
	private:
		Parameter mParam;
		arma::imat mPGrid;
		arma::imat mQGrid;

		arma::cx_mat mKxNorm;
		arma::cx_mat mKyNorm;
		arma::cx_mat mKzRefNorm;
		arma::cx_mat mKzTrnNorm;

		arma::cx_vec mCIncSPol;
		arma::cx_vec mCIncPPol;
		

		void mBuildMe();
		void mBuildGrids();
		void mBuildKxyNorm();
		void mBuildKzRefTrn();
		void mCalcSPol();
		arma::cx_mat mBuildKzNormSqrt(std::complex<double> preFaktor);

	};

}

