import numpy as np
from scipy.stats import norm

# Modèle de Black-Scholes
# Utilisé pour les options européennes où la volatilité est supposée constante dans le temps.
# Très utilisé pour des options standards sur actions, indices ou devises, en raison de sa simplicité et de sa formule fermée.
# Il assume une volatilité constante et une dynamique du sous-jacent suivant un mouvement brownien géométrique.

class BS_pricer:
    def __init__(self, S, K, T, r, sigma):
        self.S = S          # Prix de l'actif sous-jacent
        self.K = K          # Prix d'exercice
        self.T = T          # Maturité
        self.r = r          # Taux sans risque
        self.sigma = sigma  # Volatilité

    def get_european_option(self):
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        call_price = self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        return call_price, put_price

    def get_asian_option(self):
        sigma_adj = self.sigma / np.sqrt(3)
        r_adj = 0.5 * (self.r - 0.5 * self.sigma^2) + 0.5 * ((self.sigma^2) / 3)

        d1, d2 = BS_pricer.get_BS_parameter(self.S, self.K, self.T, r_adj, sigma_adj)

        call_price = (self.S * np.exp(r_adj * self.T) * norm.cdf(d1)
                      - self.K * np.exp(-r_adj * self.T) * norm.cdf(d2))

        put_price = (self.K * np.exp(-r_adj * self.T) * norm.cdf(-d2)
                     - self.S * np.exp(-r_adj * self.T) * norm.cdf(-d1))
        return call_price, put_price
