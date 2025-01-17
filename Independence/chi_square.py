from scipy.stats import chi2
import numpy as np

def chi_sqare(table, p_value=0.05):
    X_p = chi2.ppf(q=1-p_value, df=1)

    a = np.double(table[0][0])
    b = np.double(table[0][1])
    c = np.double(table[1][0])
    d = np.double(table[1][1])
    n = a + b + c + d
    if a+b == 0:
        return True
    if c+d == 0:
        return True
    if a+c == 0:
        return True
    if b+d == 0:
        return True
    # if min(a, b, c, d) < 5:
    #     return True
    X = n * (a * d - b * c)**2 / ((a+b) * (c+d) * (a+c) * (b+d))
    # print(X)

    if X > X_p:
        return False
    else:
        return True