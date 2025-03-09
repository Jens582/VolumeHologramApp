#include "CalculatorDiffractionEfficiency.h"
#include "SystemParameters.h"
#include "ScatterMatrix.h"

#include <armadillo>
#include <string>


namespace {
    void calculateAndFillDiffractionEfficiency(arma::mat& Tout, arma::mat& Rout, const rcwa::SystemParameters& system,const rcwa::ScatterMatrix& S, const arma::cx_vec& cInc);
}


namespace rcwa {

    DiffractionEfficiency::DiffractionEfficiency() {};

    void DiffractionEfficiency::print(const std::string& msg) const {
        std::cout << msg << std::endl;
        RS.print("Rs");
        RP.print("Rp");
        TS.print("Ts");
        TP.print("Tp");
    }

    DiffractionEfficiency calculateDiffractionEfficiency(const SystemParameters& system, const ScatterMatrix& S) {
        DiffractionEfficiency efficiency;
        const arma::cx_vec& cIncSPol = system.cIncSPol;
        const arma::cx_vec& cIncPPol = system.cIncPPol;
        calculateAndFillDiffractionEfficiency(efficiency.TS, efficiency.RS, system, S, cIncSPol);
        calculateAndFillDiffractionEfficiency(efficiency.TP, efficiency.RP, system, S, cIncPPol);
        return efficiency;
    }
}

namespace {

	void calculateAndFillDiffractionEfficiency(arma::mat& Tout, arma::mat& Rout, const rcwa::SystemParameters& system,const rcwa::ScatterMatrix& S,const arma::cx_vec& cInc) {

        const arma::cx_mat& kxn = system.kxNorm;
        const arma::cx_mat& kyn = system.kyNorm;

        const arma::cx_mat& kZRef = system.kzRefNorm;
        const arma::cx_mat& kZTrn = system.kzTrnNorm;

        int dim = kxn.n_rows;
        arma::cx_vec cRef = S.s11 * cInc;
        arma::cx_vec cTrn = S.s21 * cInc;

        arma::cx_vec rX = cRef.subvec(0, dim - 1);
        arma::cx_vec rY = cRef.subvec(dim, 2*dim-1);

        arma::cx_vec tX = cTrn.subvec(0, dim - 1);
        arma::cx_vec tY = cTrn.subvec(dim, 2 * dim - 1);

        arma::cx_vec rZ = (-arma::inv(kZRef)) * ((kxn * rX) + (kyn * rY));
        arma::cx_vec tZ = (-arma::inv(kZTrn)) * ((kxn * tX) + (kyn * tY));

        arma::vec RTemp = arma::pow(arma::abs(rX), 2) + arma::pow(arma::abs(rY), 2) + arma::pow(arma::abs(rZ), 2);
        arma::vec TTemp = arma::pow(arma::abs(tX), 2) + arma::pow(arma::abs(tY), 2) + arma::pow(arma::abs(tZ), 2);
        
        int dimX = 2*system.param.harmonicOrderX+1;
        int dimY = 2*system.param.harmonicOrderY+1;

        arma::mat pre = arma::real(-(kZRef / system.param.urRef));
        std::complex<double> kznInc = system.param.kzInc / system.param.k0;
        double down = (kznInc / system.param.urRef).real();
        pre /= down;
        Rout = arma::reshape(100.0 * pre * RTemp, dimX, dimY).t();


        pre = arma::real((kZTrn / system.param.urTrn));                
        pre /= down;
        Tout = arma::reshape(100.0 * pre * TTemp, dimX, dimY).t();

	}

}

