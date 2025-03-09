#pragma once
#include <armadillo>
#include "DeviceCreator.h"

namespace rcwa {

	struct HoeWriterParameter {
		double lamHoe{ 0.5 };
		double thetaDegRec1{ 30.0 };
		double phiDegRec1{ 0.0 };
		double thetaDegRec2{ 60 };
		double phiDegRec2{ 0.0 };
		double n{ 1.5 };
		double dn{ 0.001 };

		bool stepsPerCycle{ true };
		double thickness{ 100.0 };

		bool addArLayer{ true };
		double thetaDeg{ 45.0 };
		double dimZ;
	};
	
	class HoeWriter : public DeviceCreator
	{
	public:
		HoeWriter();
		HoeWriter(const HoeWriterParameter& writerParameter);
		void setWriterParameter(const HoeWriterParameter& writerParameter);
		
		void fillLayerdata(LayerData& layerData, int index) const override;
		int getIndividuallyLayerCount() const override;

		int getDimZ()const;
		double getCycleLengthZDirection() const;
		double getDz() const;
		double getAngleCoordinateRotation() const;
		double getBuildThicknessRest() const;

		const arma::vec& getGratingVector() const;
		const arma::vec& getGratingVectorRot() const;
		const std::vector<int>& getThicknessInPowerOfTwoCycles() const;


	private:
		HoeWriterParameter mWriterParameter;
		double mAngleCoordinateRotation;
		arma::vec mGratingVector;
		arma::vec mGratingVectorRot;
		arma::cx_mat mXYGrid;
		std::vector<int> mThicknessInPowerOfTwoCycles;
		double mThicknessRest;
		double mDz;

		void mfillLayerdataAr(LayerData& layerData) const;

		void mBuildMe();
		void mBuildGratingVectors();
		void mBuildAngleCoordinateRotation();
		void mBuildGrid();
		void mBuildThicknessInPowerOfTwoCycles();
		void mBuildThicknessRest();

		arma::vec mCalcKInMaterie(double thetaDeg, double phiDeg);


	};

}

