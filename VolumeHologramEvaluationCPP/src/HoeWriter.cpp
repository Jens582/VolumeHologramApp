#include "HoeWriter.h"
#include "constants.h"
#include <armadillo>
#include <stdexcept>
#include <iostream>
#include <numbers>
#include <numeric>

namespace rcwa {

	HoeWriter::HoeWriter(){}

	HoeWriter::HoeWriter(const HoeWriterParameter& writerParameter):mWriterParameter(writerParameter) {
		mBuildMe();
	}
	void HoeWriter::setWriterParameter(const HoeWriterParameter& writerParameter) {
		mWriterParameter = writerParameter;
		mBuildMe();
	}

	void HoeWriter::fillLayerdata(LayerData& layerData, int index) const{
		int count = getIndividuallyLayerCount();
		if (index < 0) { return; }
		if (index >= count) { return; }
		
		layerData.ur = arma::cx_mat(mXYGrid.n_rows, mXYGrid.n_cols, arma::fill::ones);

		if ((index == count-1) && mWriterParameter.addArLayer)
		{
			mfillLayerdataAr(layerData);
			return;
		}
		double zKz = index * mDz*mGratingVectorRot(2);
		layerData.er = arma::pow(mWriterParameter.dn * arma::cos(mXYGrid * mGratingVectorRot(0)+zKz)+ mWriterParameter.n, 2);
		layerData.identifier = std::to_string(index);
		layerData.li = mDz;
	}

	int HoeWriter::getIndividuallyLayerCount() const {
		if (mWriterParameter.addArLayer) { return mWriterParameter.dimZ + 1; }
		return mWriterParameter.dimZ;
	}

	int HoeWriter::getDimZ() const {
		return mWriterParameter.dimZ;
	}

	double HoeWriter::getCycleLengthZDirection() const {
		double gz = abs(mGratingVectorRot[2]);
		return pi2 / gz;
	}

	double HoeWriter::getDz() const {
		return mDz;
	}

	double HoeWriter::getAngleCoordinateRotation() const {
		return mAngleCoordinateRotation;
	}

	double HoeWriter::getBuildThicknessRest() const {
		return mThicknessRest;
	}


	const arma::vec& HoeWriter::getGratingVector() const{
		return mGratingVector;
	}
	const arma::vec& HoeWriter::getGratingVectorRot() const{
		return mGratingVectorRot;
	}

	const std::vector<int>& HoeWriter::getThicknessInPowerOfTwoCycles() const {
		return mThicknessInPowerOfTwoCycles;
	}

	
	
	// private

	void HoeWriter::mfillLayerdataAr(LayerData& layerData) const {
		double nAr = std::sqrt(mWriterParameter.n);
		double theta = mWriterParameter.thetaDeg * degToRad;
		double sinAr = std::sin(theta) / nAr;
		double cosAr = std::sqrt(1 - (sinAr * sinAr));
		double l = mWriterParameter.lamHoe / (4.0 * nAr * cosAr);
		std::complex<double> nArC = { nAr,0.0 };
		layerData.er = nArC* nArC;
		layerData.li = l;
		layerData.identifier = "ar";
	}

	void HoeWriter::mBuildMe() {
		mBuildGratingVectors();
		mBuildAngleCoordinateRotation();
		mBuildGrid();
		mBuildThicknessInPowerOfTwoCycles();
		mBuildThicknessRest();
	}

	void HoeWriter::mBuildGratingVectors() {
		arma::vec k1 = mCalcKInMaterie(mWriterParameter.thetaDegRec1, mWriterParameter.phiDegRec1);
		arma::vec k2 = mCalcKInMaterie(mWriterParameter.thetaDegRec2, mWriterParameter.phiDegRec2);
		mGratingVector = k1 - k2;

		double gx = mGratingVector[0];
		double gy = mGratingVector[1];
		double gz = mGratingVector[2];
		double gPre = std::sqrt((gx * gx) + (gy * gy));
		mGratingVectorRot = { gPre, 0.0, gz };
	}

	void HoeWriter::mBuildAngleCoordinateRotation() {
		arma::vec& g = mGratingVector;
		double rad = std::atan2(g[1], g[0]);
		mAngleCoordinateRotation =  rad / degToRad;
	}

	void HoeWriter::mBuildGrid() {
		arma::vec& g = mGratingVectorRot;
		int nx = 101;
		double dx = 1.0;

		if (std::abs(g[0]) < 1e-8) {
			nx = 3;
			dx = 100.0 * mWriterParameter.lamHoe / nx;
		}
		else
		{
			nx = 101;
			double l = std::abs(pi2 / g[0]);
			dx = l / nx;
		}

		if (mWriterParameter.stepsPerCycle)
		{
			if (std::abs(g[2]) < 1e-8) {
				throw std::runtime_error("Grating vector in z - direction is too small.Do not set nz_steps_per_cycle");
			}
			double l = std::abs(pi2 / g[2]);			
			mDz = l / mWriterParameter.dimZ;
		}
		else {
			mDz = mWriterParameter.thickness / mWriterParameter.dimZ;
		}
		mXYGrid.set_size(3, nx);
		arma::vec vx = arma::regspace(0.0, nx - 1) * dx;
		arma::cx_vec cx_vx = arma::cx_vec(vx, arma::zeros<arma::vec>(vx.n_elem));
		mXYGrid = arma::repmat(cx_vx.t(), 3, 1);
	}

	void HoeWriter::mBuildThicknessInPowerOfTwoCycles() {
		
		if (!mWriterParameter.stepsPerCycle) {
			mThicknessInPowerOfTwoCycles.push_back(0);
			return;
		}
		double length = getCycleLengthZDirection();
		int n = int(mWriterParameter.thickness / length);
		if (n == 0) {
			return;
		}
		bool more = true;
		while (more) {
			int x = int(std::log2(n));
			mThicknessInPowerOfTwoCycles.push_back(x);
			n -= 1 << x;
			if (n == 0) {
				more = false;
			}
		}
		std::sort(mThicknessInPowerOfTwoCycles.begin(), mThicknessInPowerOfTwoCycles.end());
	}
	
	void HoeWriter::mBuildThicknessRest() {
		mThicknessRest = std::nan("");
		if (!mWriterParameter.stepsPerCycle) {
			return;
		}
		double length = getCycleLengthZDirection();
		int sum = std::accumulate(mThicknessInPowerOfTwoCycles.begin(), mThicknessInPowerOfTwoCycles.end(), 0,
			[](int acc, int p) { return acc + (1 << p); });
		mThicknessRest = mWriterParameter.thickness - sum * length;
	}

	arma::vec HoeWriter::mCalcKInMaterie(double thetaDeg, double phiDeg) {
		double k0 = pi2 / mWriterParameter.lamHoe;
		double kx = k0 * std::sin(degToRad * thetaDeg) * std::cos(degToRad * phiDeg);
		double ky = k0 * std::sin(degToRad * thetaDeg) * std::sin(degToRad * phiDeg);
		double kz = std::sqrt((mWriterParameter.n * mWriterParameter.n * k0 * k0) - (kx * kx) - (ky * ky));
		return { kx, ky, kz };
	}
}
