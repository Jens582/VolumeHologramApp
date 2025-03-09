#include "CalcAllScatterMatrices.h"
#include "SystemParameters.h"
#include "DeviceCreator.h"
#include "ScatterMatrix.h"
#include "EigenValuesVectors.h"
#include <armadillo>
#include <map>
#include <array>
#include <complex>

#include <stdexcept>
#include <string>


namespace {
    std::array<arma::cx_mat, 2> mEigenVectorsVacuumV0W0(const rcwa::SystemParameters& system);

    rcwa::ScatterMatrix mBuildScatterMatrixInsideVacuum(const rcwa::EigenValuesVectors& eigen, const arma::cx_mat& v0, const arma::cx_mat& w0);

    std::array<rcwa::ScatterMatrix, 2> mCalculateScatterRefTrn(const rcwa::SystemParameters& system, const arma::cx_mat& v0, const arma::cx_mat& w0);

}



namespace rcwa
{
    std::map<std::string, ScatterMatrix> calcAllScatterMatricesOfSystem(const SystemParameters& system) {
        std::array<arma::cx_mat, 2> v0w0 = mEigenVectorsVacuumV0W0(system);
        arma::cx_mat& v0 = v0w0[0];
        arma::cx_mat& w0 = v0w0[1];

        std::map<std::string, ScatterMatrix> matrices;
        int num = system.deviceCreator->getIndividuallyLayerCount();

        LayerData layerData;
        for (int i = 0; i < num; i++)
        {
            system.deviceCreator->fillLayerdata(layerData, i);
            EigenValuesVectors eigen(system, layerData);

            std::string identifier = layerData.identifier;
            ScatterMatrix t = mBuildScatterMatrixInsideVacuum(eigen, v0, w0);
            matrices.insert({ identifier, t });
        }

        std::array<ScatterMatrix, 2> refTrn = mCalculateScatterRefTrn(system, v0, w0);
        matrices.insert({ "sRef", refTrn[0] });
        matrices.insert({ "sTrn", refTrn[1] });
        return matrices;
    }
}

namespace{

    std::array<arma::cx_mat, 2> mEigenVectorsVacuumV0W0(const rcwa::SystemParameters& system) {
        std::complex<double> vac = { 1.0, 0.0 };
        rcwa::LayerData layerData;
        layerData.er = vac;
        layerData.ur = vac;
        layerData.li = 1;
        rcwa::EigenValuesVectors eigen(system, layerData);
        std::array<arma::cx_mat, 2> v0W0 = { eigen.getV(), eigen.getW() };        
        return v0W0;
    }

    rcwa::ScatterMatrix mBuildScatterMatrixInsideVacuum(const rcwa::EigenValuesVectors& eigen, const arma::cx_mat& v0, const arma::cx_mat& w0) {
        const arma::cx_mat& vi = eigen.getV();
        const arma::cx_mat& wi = eigen.getW();        
        const arma::cx_mat& arg = eigen.getArg();

        arma::cx_mat viInv = arma::inv(vi);
        arma::cx_mat wiInv = arma::inv(wi);

        arma::cx_mat a = (wiInv * w0) + (viInv * v0);
        arma::cx_mat b = (wiInv * w0) - (viInv * v0);
        arma::cx_mat aInv = arma::inv(a);
        arma::cx_mat x = arma::expmat(arg);


        arma::cx_mat mul = arma::inv(a - (x * b * aInv * x * b));
        arma::cx_mat s11Second = (x * b * aInv * x * a) - b;
        arma::cx_mat s12Second = x * (a - (b * aInv * b));

        arma::cx_mat s11 = mul * s11Second;
        arma::cx_mat s12 = mul* s12Second;

        rcwa::ScatterMatrix s;
        s.s11 = s11;
        s.s12 = s12;
        s.s22 = s11;
        s.s21 = s12;
        return s;
    }

    std::array<rcwa::ScatterMatrix, 2> mCalculateScatterRefTrn(const rcwa::SystemParameters& system, const arma::cx_mat& v0, const arma::cx_mat& w0) {
        
        rcwa::LayerData layerDataRef;
        layerDataRef.er = system.param.erRef;
        layerDataRef.ur = system.param.urRef;
        layerDataRef.li = 1.0;
        rcwa::EigenValuesVectors eigenRef(system, layerDataRef);        

        rcwa::LayerData layerDataTrn;
        layerDataTrn.er = system.param.erTrn;
        layerDataTrn.ur = system.param.urTrn;
        layerDataTrn.li = 1.0;
        rcwa::EigenValuesVectors eigenTrn(system, layerDataTrn);
        
        const arma::cx_mat& vRef = eigenRef.getV();
        const arma::cx_mat& wRef = eigenRef.getW();
        const arma::cx_mat& vTrn = eigenTrn.getV();
        const arma::cx_mat& wTrn = eigenTrn.getW();

        arma::cx_mat v0Inv = arma::inv(v0);
        arma::cx_mat w0Inv = arma::inv(w0);

        arma::cx_mat aRef = (w0Inv * wRef) + (v0Inv * vRef);
        arma::cx_mat bRef = (w0Inv * wRef) - (v0Inv * vRef);
        arma::cx_mat aRefInv = arma::inv(aRef);

        arma::cx_mat aTrn = (w0Inv * wTrn) + (v0Inv * vTrn);
        arma::cx_mat bTrn = (w0Inv * wTrn) - (v0Inv * vTrn);
        arma::cx_mat aTrnInv = arma::inv(aTrn);

        rcwa::ScatterMatrix sRef;
        sRef.s11 = -(aRefInv * bRef);
        sRef.s12 = 2 * aRefInv;
        sRef.s21 = 0.5 * (aRef - (bRef * aRefInv * bRef));
        sRef.s22 = bRef * aRefInv;

        rcwa::ScatterMatrix sTrn;
        sTrn.s11 = bTrn * aTrnInv;
        sTrn.s12 = 0.5 * (aTrn - (bTrn * aTrnInv * bTrn));
        sTrn.s21 = 2 * aTrnInv;
        sTrn.s22 = -(aTrnInv * bTrn);
        std::array<rcwa::ScatterMatrix, 2> sRefTrn = { sRef, sTrn };

        return sRefTrn;
    }
    
}
