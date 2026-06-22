# file: bs_module.pyx
from libc.math cimport log, exp, sqrt, erf

# Внутренняя быстрая Си-функция для нормального распределения
cdef double std_norm_cdf(double x) noexcept:
    return 0.5 * (1.0 + erf(x / 1.4142135623730951))

# Главная функция, которую мы будем вызывать из основного бота
def calculate_black_scholes_cython(double S, double K, double r, double sigma, double T, str option_type):
    if T <= 0:
        if option_type == 'Call' or option_type == 'call':
            return max(0.0, S - K)
        else:
            return max(0.0, K - S)
            
    # cdef double — это создание переменных прямо в оперативной памяти как в Си
    cdef double d1 = (log(S / K) + (r + (sigma * sigma) / 2.0) * T) / (sigma * sqrt(T))
    cdef double d2 = d1 - sigma * sqrt(T)
    
    if option_type == 'Call' or option_type == 'call':
        return S * std_norm_cdf(d1) - K * exp(-r * T) * std_norm_cdf(d2)
    else:
        return K * exp(-r * T) * (1.0 - std_norm_cdf(d2)) - S * (1.0 - std_norm_cdf(d1))
