#pragma once
#include "Parameter.h"
#include "LayerData.h"
#include <numbers>
#include <armadillo>

namespace rcwa {
	class DeviceCreator
	{
	public:
		virtual int getIndividuallyLayerCount() const = 0;
		virtual void fillLayerdata(LayerData& layerData, int index) const = 0;
	};
}

