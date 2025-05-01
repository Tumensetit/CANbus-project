from diffprivlib.tools import quantile, mean
from diffprivlib.utils import PrivacyLeakWarning

import warnings

# NOTE:
# This function is non-incremental
# It assumes it will be called only once.
# This means the values will be off for datasets that cause the program to count stats incrementally
def diffpriv_nonincremental_mean(key, data):
    # Experimental diffpriv values
    epsilon = 1.0
    # Estimate lower and upper bounds privately
    # TODO: Differential privacy ei toimi näin. Tämä on riski yksityisyydelle. Mietittävä, miten tämä oikeasti pitäisi toteutttaa
    try:
        warnings.filterwarnings("ignore", category=PrivacyLeakWarning)
        lower_bound = quantile(data, 0.05, epsilon=epsilon)
        upper_bound = quantile(data, 0.95, epsilon=epsilon)
        warnings.resetwarnings()
        if lower_bound > upper_bound:
            lower_bound, upper_bound = upper_bound, lower_bound

        dp_mean = mean(data, epsilon=epsilon, bounds=(lower_bound, upper_bound))
    except Exception as e:
        print(f"{key}: Error occurred when calculating experimental DiffPriv mean: {e}")
        return "ERROR"

    return dp_mean
