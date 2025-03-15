from diffprivlib.tools import quantile, mean
from diffprivlib.utils import PrivacyLeakWarning

import warnings




def diffpriv_stats(key, data):
    # Experimental diffpriv values
    epsilon = 1.0
    # Estimate lower and upper bounds privately
    # TODO: Differential privacy ei toimi näin. Tämä on riski yksityisyydelle. Mietittävä, miten tämä oikeasti pitäisi toteutttaa
    warnings.filterwarnings("ignore", category=PrivacyLeakWarning)
    lower_bound = quantile(data, 0.05, epsilon=epsilon)
    upper_bound = quantile(data, 0.95, epsilon=epsilon)
    warnings.resetwarnings()
    if lower_bound > upper_bound:
        lower_bound, upper_bound = upper_bound, lower_bound
    dp_mean = mean(data, epsilon=epsilon, bounds=(lower_bound, upper_bound))
    print(f"Experimental: Differentially Private Mean: {key}, {dp_mean}")
