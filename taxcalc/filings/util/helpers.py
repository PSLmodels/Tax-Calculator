from taxcalc import Behavior, Calculator, Consumption, Growth, Policy, Records


def create_calculator(records, start_year,
                      policy=None, econ=None, sync_years=True):
    """
    Create a new calculator given a records object and a starting year.
    Optionally attach policy and economic config from files.
    """
    (policy_dict, behavior_dict, consumption_dict, growth_dict) = \
        Calculator.read_json_param_files(policy, econ)

    policy = Policy()
    policy.implement_reform(policy_dict)
    policy.set_year(start_year)
    behavior = Behavior()
    behavior.update_behavior(behavior_dict)
    consumption = Consumption()
    consumption.update_consumption(consumption_dict)
    growth = Growth()
    growth.update_growth(growth_dict)

    return Calculator(
        growth=growth, behavior=behavior, consumption=consumption,
        policy=policy, records=records, verbose=True, sync_years=sync_years
    )
