#include "HoeEvaluation.h"
#include <iostream>

/*

-----Indices ----
0) thetaDeg
1) phiDeg
2) lam
3) lamHoe
4) thetaDegRec1
5) phiDegRec1
6) thetaDegRec2
7) phiDegRec2
8) thickness
9) n
10) dn
11) dimZ
12) stepsPerCycle
13) addArLayer

*/

namespace rcwa {

	HoeEvaluation::HoeEvaluation(){
	}
		
	void HoeEvaluation::setFileNameInput(std::string name) {
		mFileNameInput = name;
	}

	void HoeEvaluation::setFileNameEvaluation(std::string name) {
		mFileNameEvaluation = name;
	}

	void HoeEvaluation::evaluateWithMessage() {
		mInfoMessageAndSaveInterval();
		evaluate();
	}

	void HoeEvaluation::evaluate() {
		mReadInputValues();		
		arma::rowvec vec;
		arma::rowvec resultsVec;
		int subIndex = 0;
		mResults.save(mFileNameEvaluation, arma::raw_ascii);
		mIndex = -1;
		mSetResultsMat();

		for (mIndex = 0; mIndex < mInputValues.n_rows; mIndex++)
		{
			vec = mInputValues.row(mIndex);
			resultsVec = mFillHoeWithInput(vec);
			mResults.row(subIndex) = resultsVec;
			subIndex++;

			if (subIndex == mResults.n_rows) {
				std::cout << "Save values" << std::endl;
				std::cout << "Calculated: " << mIndex + 1 << "  from: " << mInputValues.n_rows << std::endl;
				std::ofstream file(mFileNameEvaluation, std::ios::app);
				mResults.save(file, arma::raw_ascii);
				file.close();
				mSetResultsMat();
				subIndex = 0;
			}

		}

	}

	void HoeEvaluation::mInfoMessageAndSaveInterval() {
		std::cout << "Hoe Evaluation:\nInput values will be read from " << mFileNameInput << std::endl;
		std::cout << "Input(row) order:" << std::endl;
		std::cout << "0) thetaDeg" << std::endl;
		std::cout << "1) phiDeg" << std::endl;
		std::cout << "2) lam" << std::endl;
		std::cout << "3) lamHoe" << std::endl;
		std::cout << "4) thetaDegRec1" << std::endl;
		std::cout << "5) phiDegRec1" << std::endl;
		std::cout << "6) thetaDegRec2" << std::endl;
		std::cout << "7) phiDegRec2" << std::endl;
		std::cout << "8) thickness" << std::endl;
		std::cout << "9) n" << std::endl;
		std::cout << "10) dn" << std::endl;
		std::cout << "11) dimZ" << std::endl;
		std::cout << "12) stepsPerCycle" << std::endl;
		std::cout << "13) addArLayer" << std::endl;
		std::cout << "Enter save interval: " << std::endl;
		std::cin >> mSaveInterval;
		std::cout << "Enter harmonic order:" << std::endl;
		std::cin >> mHarmonicOrder;
		std::cout << "Start Evaluation!" << std::endl;
	}

	void HoeEvaluation::mReadInputValues() {
		mInputValues.load(mFileNameInput);
	}

	arma::rowvec HoeEvaluation::mFillHoeWithInput(const arma::rowvec& input) {
		int dimX = (2 * mHarmonicOrder + 1) * 4;		
		mHoePram.harmonicOrder = mHarmonicOrder;
		mHoePram.thetaDeg = input(0);
		mHoePram.phiDeg = input(1);
		mHoePram.lam = input(2);
		mHoePram.lamHoe = input(3);
		mHoePram.thetaDegRec1 = input(4);
		mHoePram.phiDegRec1 = input(5);
		mHoePram.thetaDegRec2 = input(6);
		mHoePram.phiDegRec2 = input(7);
		mHoePram.thickness = input(8);
		mHoePram.n = input(9);
		mHoePram.dn = input(10);
		mHoePram.dimZ = input(11);
		mHoePram.stepsPerCycle = input(12);
		mHoePram.addArLayer = input(13);

		mHoe.setParameter(mHoePram);

		arma::rowvec vec = mHoe.calculateRCWAAsRow();
		return vec;

	}


	void HoeEvaluation::mSetResultsMat() {
		int remainCalulation = mInputValues.n_rows - (mIndex+1);
		int dim = mSaveInterval;
		if (remainCalulation < mSaveInterval) {
			dim = remainCalulation;
		}
		int dimX = (2 * mHarmonicOrder + 1) * 4;
		mResults = arma::mat(dim, dimX, arma::fill::zeros);
	}

}