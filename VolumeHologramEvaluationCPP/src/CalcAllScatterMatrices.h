#pragma once
#include "SystemParameters.h"
#include "DeviceCreator.h"
#include "ScatterMatrix.h"
#include "EigenValuesVectors.h"
#include <armadillo>
#include <map>
#include <array>


namespace rcwa
{
    std::map<std::string, ScatterMatrix> calcAllScatterMatricesOfSystem(const SystemParameters& system);

}


