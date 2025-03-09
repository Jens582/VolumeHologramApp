#pragma once
#include "VolumeHologram3D.h"
#include <armadillo>
#include <string>


namespace rcwa{


	class HoeEvaluation
	{
	public:
		HoeEvaluation();
		void setFileNameInput(std::string name);
		void setFileNameEvaluation(std::string name);

		void evaluateWithMessage();
		void evaluate();
		

	private:
		rcwa::VolumeHologram3D mHoe{};
		rcwa::VolumeHologram3DParameter mHoePram{};
		std::string mFileNameInput = "hoeInputvalues.dat";
		std::string mFileNameEvaluation = "hoeEvaluation.dat";
		int mIndex;
		int mHarmonicOrder{1};

		arma::mat mInputValues{};
		arma::mat mResults{};
		int mSaveInterval{ 100 };

		arma::rowvec mFillHoeWithInput(const arma::rowvec& input);
		void mReadInputValues();
		void mInfoMessageAndSaveInterval();		
		void mSetResultsMat();
	};

}
