#pragma once
#include "Parameter.h"
#include "SystemParameters.h"
#include "HoeWriter.h"
#include <complex>
#include "ScatterMatrix.h"
#include "CalculatorDiffractionEfficiency.h"
#include <optional>

namespace rcwa {

	struct VolumeHologram3DParameter{
		double thetaDeg{45.0};
		double phiDeg{0.0};
		double lam{0.5};
		int harmonicOrder{2};
		std::complex<double> erTrn{ 1.0,0.0 };
		std::complex<double> urTrn{ 1.0,0.0 };

		//Writer
		double lamHoe{0.5}; 
		double thetaDegRec1{45.0};
		double phiDegRec1{0.0};
		double thetaDegRec2{20.0};
		double phiDegRec2{0.0};
		double n{1.5}; 
		double dn{0.01};
		int dimZ{101};
		bool stepsPerCycle{true};
		double thickness{100}; 
		bool addArLayer{true}; 
	};


	class VolumeHologram3D 
	{
	public:
		VolumeHologram3D();
		VolumeHologram3D(const VolumeHologram3DParameter& pram);
		void setParameter(const VolumeHologram3DParameter& pram);
		DiffractionEfficiency calculateRCWA();
		arma::rowvec calculateRCWAAsRow();
		
	private:
		VolumeHologram3DParameter mPram;

		std::shared_ptr<HoeWriter> mGetHoeWriter();
		SystemParameters mGetSystemParameter();		
		std::map<std::string, ScatterMatrix> mGetAccumulatedScatterMatrices(const SystemParameters& system);	
		ScatterMatrix mCalcPowerScatterMatrix(const SystemParameters& system, std::map<std::string, ScatterMatrix>& accumulatedMatrices);
		ScatterMatrix mCalcRestScatterMatrix(const SystemParameters& system, std::map<std::string, ScatterMatrix>& accumulatedMatrices);
		ScatterMatrix mCalcGlobalScatterMatrix(const ScatterMatrix& powerMatrix, const ScatterMatrix& restMatrix, std::map<std::string, ScatterMatrix>& accumulatedMatrices);
				
		static std::string mFindClosed(std::map<std::string, ScatterMatrix>& accumulatedMatrices, double rest);
		static bool mIsNumber(const std::string& s);
	};


}
