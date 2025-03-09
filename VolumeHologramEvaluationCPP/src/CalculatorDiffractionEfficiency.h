#pragma once
#include "SystemParameters.h"
#include "ScatterMatrix.h"

#include <armadillo>
#include <string>


namespace rcwa{

struct DiffractionEfficiency {
	DiffractionEfficiency();
	arma::mat RS{};
	arma::mat RP{};
	arma::mat TS{};
	arma::mat TP{};
	void print(const std::string& msg) const;
};

DiffractionEfficiency calculateDiffractionEfficiency(const SystemParameters& system, const ScatterMatrix& S);

}


