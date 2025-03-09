#pragma once
#include <numbers>
#include <armadillo>
#include <string>

namespace rcwa {
	struct LayerData
	{
		arma::cx_mat er{};
		arma::cx_mat ur{};
		double li{};
		std::string identifier = "";
	};
}
