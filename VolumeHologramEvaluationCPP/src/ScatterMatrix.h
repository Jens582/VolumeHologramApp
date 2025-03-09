#pragma once
#include <armadillo>
#include <string>

namespace rcwa{

	struct ScatterMatrix{
		ScatterMatrix();
		arma::cx_mat s11{};
		arma::cx_mat s21{};
		arma::cx_mat s12{};
		arma::cx_mat s22{};
		
		void print(const std::string& msg) const;
		static ScatterMatrix redhefferStarProduct(const ScatterMatrix& sa, const ScatterMatrix& sb);
		static ScatterMatrix Unity(int dimSij);
	};

}