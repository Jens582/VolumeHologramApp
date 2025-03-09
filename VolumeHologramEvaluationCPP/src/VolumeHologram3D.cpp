#include "VolumeHologram3D.h"
#include "SystemParameters.h"
#include "CalcAllScatterMatrices.h"
#include "ScatterMatrix.h"
#include "HoeWriter.h"
#include "constants.h"
#include <numbers>
#include <armadillo>
#include <algorithm>  
#include <numeric>

namespace rcwa {

	VolumeHologram3D::VolumeHologram3D(){};
	VolumeHologram3D::VolumeHologram3D(const VolumeHologram3DParameter& pram): mPram(pram) {}
	void VolumeHologram3D::setParameter(const VolumeHologram3DParameter& pram) { mPram = pram; }

	DiffractionEfficiency VolumeHologram3D::calculateRCWA() {
		rcwa::SystemParameters system = mGetSystemParameter();		
		std::map<std::string, rcwa::ScatterMatrix> accumulatedMatrices = mGetAccumulatedScatterMatrices(system);
		rcwa::ScatterMatrix powerMatrix = mCalcPowerScatterMatrix(system, accumulatedMatrices);
		rcwa::ScatterMatrix restMatrix = mCalcRestScatterMatrix(system, accumulatedMatrices);		
		rcwa::ScatterMatrix globalMatrix = mCalcGlobalScatterMatrix(powerMatrix, restMatrix, accumulatedMatrices);
		rcwa::DiffractionEfficiency efficieny = rcwa::calculateDiffractionEfficiency(system, globalMatrix);
		return efficieny;
	}

	arma::rowvec VolumeHologram3D::calculateRCWAAsRow() {
		DiffractionEfficiency efficieny = calculateRCWA();
		arma::rowvec vec;
		vec = arma::join_horiz(vec, arma::vectorise(efficieny.RS.t()).t());
		vec = arma::join_horiz(vec, arma::vectorise(efficieny.RP.t()).t());
		vec = arma::join_horiz(vec, arma::vectorise(efficieny.TS.t()).t());
		vec = arma::join_horiz(vec, arma::vectorise(efficieny.TP.t()).t());
		return vec;
	}

	std::shared_ptr<HoeWriter> VolumeHologram3D::mGetHoeWriter() {
		auto writer = std::make_shared<HoeWriter>();
		HoeWriterParameter pramWriter;
		pramWriter.dimZ = mPram.dimZ;
		pramWriter.lamHoe = mPram.lamHoe;
		pramWriter.thetaDegRec1 = mPram.thetaDegRec1;
		pramWriter.phiDegRec1 = mPram.phiDegRec1;
		pramWriter.thetaDegRec2 = mPram.thetaDegRec2;
		pramWriter.phiDegRec2 = mPram.phiDegRec2;
		pramWriter.n = mPram.n;
		pramWriter.dn = mPram.dn;
		pramWriter.stepsPerCycle = mPram.stepsPerCycle;
		pramWriter.thickness = mPram.thickness;
		pramWriter.addArLayer = mPram.addArLayer;
		pramWriter.thetaDeg = mPram.thetaDeg;

		writer->setWriterParameter(pramWriter);
		return writer;
	}

	SystemParameters VolumeHologram3D::mGetSystemParameter() {
		std::shared_ptr<HoeWriter> writer = mGetHoeWriter();
		double anglePhiRotation = writer->getAngleCoordinateRotation();
		double k0 = pi2 / mPram.lam;
		double phiRot = mPram.phiDeg - anglePhiRotation;
		std::complex<double> kxInc = { k0 * std::sin(degToRad * mPram.thetaDeg) * std::cos(degToRad * phiRot), 0.0 };
		std::complex<double> kyInc = { k0 * std::sin(degToRad * mPram.thetaDeg) * std::sin(degToRad * phiRot), 0.0 };
		std::complex<double> kzInc = { k0 * std::cos(degToRad * mPram.thetaDeg), 0.0 };

		Parameter pram;
		pram.k0 = k0;
		pram.kxInc = kxInc;
		pram.kyInc = kyInc;
		pram.kzInc = kzInc;
		pram.harmonicOrderX = mPram.harmonicOrder;
		pram.harmonicOrderY = 0;

		arma::vec vec = writer->getGratingVectorRot();
		pram.t1X = std::abs(vec[0]);
		pram.t1Y = 0.0;
		pram.t2X = 0.0;
		pram.t2Y = 0.0;

		pram.erRef = { 1.0, 0.0 };
		pram.urRef = { 1.0, 0.0 };
		pram.erTrn = { 1.0, 0.0 };
		pram.urTrn = { 1.0, 0.0 };

		return SystemParameterCreator::createSystemParameters(pram, writer);
	}

	std::map<std::string, ScatterMatrix> VolumeHologram3D::mGetAccumulatedScatterMatrices(const SystemParameters& system) {
		auto ptr = std::dynamic_pointer_cast<const rcwa::HoeWriter>(system.deviceCreator);
		double dz = ptr->getDz();
		std::map<std::string, ScatterMatrix> allMatrices = calcAllScatterMatricesOfSystem(system);
		std::map<std::string, ScatterMatrix> accumulatedMatrices;
		accumulatedMatrices.insert({ "sRef", allMatrices["sRef"] });
		accumulatedMatrices.insert({ "sTrn", allMatrices["sTrn"] });
		if (mPram.addArLayer) {
			accumulatedMatrices.insert({ "ar", allMatrices["ar"] });
		}
		int dim = allMatrices["sRef"].s11.n_rows;
		ScatterMatrix device = ScatterMatrix::Unity(dim);
		double length = 0.0;
		accumulatedMatrices.insert({ std::to_string(length), device });
		for (int i = 0; i < mPram.dimZ; i++) {
			std::string key = std::to_string(i);
			ScatterMatrix& next = allMatrices[key];
			device = ScatterMatrix::redhefferStarProduct(device, next);
			length += dz;
			accumulatedMatrices.insert({ std::to_string(length), device });
		}
		accumulatedMatrices.insert({ "full", device });
		return accumulatedMatrices;
	}

	ScatterMatrix VolumeHologram3D::mCalcPowerScatterMatrix(const SystemParameters& system, std::map<std::string,  ScatterMatrix>& accumulatedMatrices) {
		auto ptrWriter = std::dynamic_pointer_cast<const rcwa::HoeWriter>(system.deviceCreator);
		std::vector<int> powers = ptrWriter -> getThicknessInPowerOfTwoCycles();
		double rest = ptrWriter -> getBuildThicknessRest();

		int dim = accumulatedMatrices["sRef"].s11.n_rows;
		ScatterMatrix device = ScatterMatrix::Unity(dim);
		ScatterMatrix temp = accumulatedMatrices["full"];

		int dimPowers = powers.size();
		
		if (dimPowers != 0)
		{
			int maxPower = *std::max_element(powers.begin(), powers.end());
			for (int x = 0; x < (maxPower + 1); x++) {

				if (x != 0) {
					temp = ScatterMatrix::redhefferStarProduct(temp, temp);
					int p = (1 << x);
				}

				if (std::find(powers.begin(), powers.end(), x) != powers.end()) {
					device = ScatterMatrix::redhefferStarProduct(device, temp);
				}
			}
		}
		return device;
	}
	
	ScatterMatrix VolumeHologram3D::mCalcRestScatterMatrix(const SystemParameters& system, std::map<std::string, ScatterMatrix>& accumulatedMatrices) {
		auto ptrWriter = std::dynamic_pointer_cast<const rcwa::HoeWriter>(system.deviceCreator);
		std::vector<int> powers = ptrWriter->getThicknessInPowerOfTwoCycles();
		double rest = ptrWriter->getBuildThicknessRest();

		if (!std::isnan(rest)) {
			std::string closest_key = mFindClosed(accumulatedMatrices, rest);
			return accumulatedMatrices[closest_key];

		}
		else {
			int dim = accumulatedMatrices["sRef"].s11.n_rows;
			return ScatterMatrix::Unity(dim);
		}

	}
		
	ScatterMatrix VolumeHologram3D::mCalcGlobalScatterMatrix(const ScatterMatrix& powerMatrix, const ScatterMatrix& restMatrix, std::map<std::string, ScatterMatrix>& accumulatedMatrices) {

		const ScatterMatrix& sRef = accumulatedMatrices["sRef"];
		const ScatterMatrix& sTrn = accumulatedMatrices["sTrn"];
		int dim = accumulatedMatrices["sRef"].s11.n_rows;

		ScatterMatrix device = ScatterMatrix::redhefferStarProduct(powerMatrix, restMatrix);

		if (mPram.addArLayer) {
			ScatterMatrix& sAr = accumulatedMatrices["ar"];
			device = ScatterMatrix::redhefferStarProduct(device, sAr);
			device = ScatterMatrix::redhefferStarProduct(sAr, device);
		}
		device = ScatterMatrix::redhefferStarProduct(device, sTrn);
		device = ScatterMatrix::redhefferStarProduct(sRef, device);
		return device;
	}


	std::string VolumeHologram3D::mFindClosed(std::map<std::string, ScatterMatrix>& accumulatedMatrices, double rest) {
		std::string bestKey;
		double minDiff = std::numeric_limits<double>::max();

		for (const auto& [key, matrix] : accumulatedMatrices) {
			if (mIsNumber(key)) {
				double keyVal = std::stod(key);
				double diff = std::abs(keyVal - rest);
				if (diff < minDiff) {
					minDiff = diff;
					bestKey = key;
				}
			}
		}

		if (bestKey.empty()) {
			throw std::runtime_error("shoud not happen");
		}
		return bestKey;
	}
	bool VolumeHologram3D::mIsNumber(const std::string& s) {
		try {
			std::stod(s);
			return true;
		}
		catch (...) {
			return false;
		}
	}

	
}

