#pragma once
#include <complex>

namespace rcwa {

	struct Parameter
	{
		double k0{};
		std::complex<double> kxInc{};
		std::complex<double> kyInc{};
		std::complex<double> kzInc{};

		int harmonicOrderX{};
		int harmonicOrderY{};

		double t1X{};
		double t1Y{};
		double t2X{};
		double t2Y{};


		std::complex<double> erRef{};
		std::complex<double> urRef{};
		std::complex<double> erTrn{};
		std::complex<double> urTrn{};

	};

}

