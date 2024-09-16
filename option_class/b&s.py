import numpy as np
from scipy.stats import norm


class BS_pricer:
    def __init__(self, S, K, T, r, sigma):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    @staticmethod
    def get_BS_parameter(S, K, T, r, sigma):
        d1 = (np.log(S/K) + (r + 0.5 * sigma^2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return d1, d2

    def get_european_option(self):
        d1, d2 = BS_pricer.get_BS_parameter(self.S, self.K, self.T, self.r, self.sigma)
        call_price = self.S * norm.cdf(d1) - self.K * norm.cdf(d2)
        put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        return call_price, put_price

    def get_asiatic_option(self):
        sigma_adj = self.sigma / np.sqrt(3)
        r_adj = 0.5 * (self.r - 0.5 * self.sigma^2) + 0.5 * ((self.sigma^2) / 3)

        d1, d2 = BS_pricer.get_BS_parameter(self.S, self.K, self.T, r_adj, sigma_adj)

        call_price = (self.S * np.exp(r_adj * self.T) * norm.cdf(d1)
                      - self.K * np.exp(-r_adj * self.T) * norm.cdf(d2))

        put_price = (self.K * np.exp(-r_adj * self.T) * norm.cdf(-d2)
                     - self.S * np.exp(-r_adj * self.T) * norm.cdf(-d1))
        return call_price, put_price
