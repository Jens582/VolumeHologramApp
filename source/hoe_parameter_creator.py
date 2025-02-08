from source.parameter import Parameter, ParameterBool, ParameterFloat, ParameterInt, ParameterCyclesThickness


def create_hoe_parameter():
    hoe_parameters: dict[str, Parameter] = dict()

    cycles_thickness = ParameterCyclesThickness(1)
    cycles_thickness.start = 100
    cycles_thickness.end = 1000
    hoe_parameters["cycles_thickness"] = cycles_thickness


    theta = ParameterFloat(0.0)
    theta.v_min = -89.0
    theta.v_max = 89.0
    theta.start = 0
    theta.end = 10
    theta.steps = 5
    theta.attribute_name = "theta_deg"
    hoe_parameters["theta"] = theta

    phi = ParameterFloat(0.0)
    phi.v_min = -360
    phi.v_max = 360
    phi.attribute_name = "phi_deg"
    hoe_parameters["phi"] = phi

    lam = ParameterFloat(0.5)
    lam.v_min = 10E-10
    lam.attribute_name = "lam"
    hoe_parameters["lam"] = lam

    theta_rec1 = ParameterFloat(45.0)
    theta_rec1.attribute_name = "theta_rec1"
    hoe_parameters["theta_rec1"] = theta_rec1

    phi_rec1 = ParameterFloat(0.0)
    phi_rec1.v_min = 0
    phi_rec1.v_max = 360
    phi_rec1.attribute_name = "phi_rec1"
    hoe_parameters["phi_rec1"] = phi_rec1

    theta_rec2 = ParameterFloat(0.0)
    theta_rec2.attribute_name = "theta_rec2"
    hoe_parameters["theta_rec2"] = theta_rec2

    phi_rec2 = ParameterFloat(0.0)
    phi_rec2.v_min = 0
    phi_rec2.v_max = 360
    phi_rec2.attribute_name = "phi_rec2"
    hoe_parameters["phi_rec2"] = phi_rec2

    lam_hoe = ParameterFloat(0.5)
    lam_hoe.v_min = 10E-10 
    lam_hoe.attribute_name = "lam_hoe"
    hoe_parameters["lam_hoe"] = lam_hoe

    n= ParameterFloat(1.5)
    n.v_min = 1.0
    n.attribute_name = "n"
    hoe_parameters["n0"] = n

    dn = ParameterFloat(0.01)
    dn.v_min = 0
    dn.attribute_name = "dn"
    hoe_parameters["dn"] = dn


    thickness = ParameterFloat(100.0)
    thickness.v_min = 0.0
    thickness.start = 0.0
    thickness.end = 100.0
    thickness.steps = 20
    thickness.attribute_name = "thickness"
    hoe_parameters["thickness"] = thickness

    nz_steps_per_cycle = ParameterBool(1)
    add_ar_layer = ParameterBool(1)

    nz_steps_per_cycle.attribute_name = "nz_steps_per_cycle"
    add_ar_layer.attribute_name = "add_ar_layer"
    hoe_parameters["add_ar_layer"] = add_ar_layer

    nz = ParameterInt(21)
    harmonic = ParameterInt(2)

    nz.is_variable = False
    harmonic.is_variable = False

    nz.v_min = 0
    harmonic.v_min = 0

    nz.attribute_name = "n_z"
    harmonic.attribute_name = "harmonic_order"

    hoe_parameters["n_z"] = nz
    hoe_parameters["nz_steps_per_cycle"] = nz_steps_per_cycle
    hoe_parameters["harmonic_order"] = harmonic
    return hoe_parameters