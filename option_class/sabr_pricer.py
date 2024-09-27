import numpy as np
from scipy.stats import norm

# Modèle SABR (Stochastic Alpha Beta Rho)
# Utilisé pour modéliser la volatilité implicite des options, en particulier pour les marchés des taux d'intérêt et des matières premières.
# Il est capable de capturer le "smile" de volatilité et permet de modéliser des dynamiques de volatilité stochastique.
# Particulièrement utilisé dans les marchés où la volatilité dépend du prix du sous-jacent et évolue dans le temps.

class SABR_pricer:
    def __init__(self, S, K, T, alpha, beta, rho, nu):
        self.S = S          # Prix actuel du sous-jacent
        self.K = K          # Prix d'exercice (strike)
        self.T = T          # Maturité
        self.alpha = alpha  # Volatilité initiale
        self.beta = beta    # Paramètre de forme (0 <= beta <= 1)
        self.rho = rho      # Corrélation entre les processus de volatilité et de prix
        self.nu = nu        # Volatilité de la volatilité

    def sabr_volatility(self):
        """Calcule la volatilité implicite approximée du modèle SABR."""
        F = self.S  # Prix Forward, supposé ici comme étant le prix spot
        if self.K == F:
            # Cas où K est égal à F (Prix forward)
            V = self.alpha * (1 + ((1 - self.beta) ** 2 / 24) * (self.alpha ** 2 / F ** (2 - 2 * self.beta)) * self.T
                              + (self.rho * self.beta * self.nu * self.alpha) / (4 * F ** (1 - self.beta)) * self.T
                              + (2 - 3 * self.rho ** 2) * (self.nu ** 2 / 24) * self.T)
        else:
            # Cas général
            z = (self.nu / self.alpha) * (F * self.K) ** ((1 - self.beta) / 2) * np.log(F / self.K)
            x_z = np.log((np.sqrt(1 - 2 * self.rho * z + z ** 2) + z - self.rho) / (1 - self.rho))

            A = self.alpha / ((F * self.K) ** ((1 - self.beta) / 2) * (1 + ((1 - self.beta) ** 2 / 24) * np.log(F / self.K) ** 2
                                                                       + ((1 - self.beta) ** 4 / 1920) * np.log(F / self.K) ** 4))

            B = 1 + ((1 - self.beta) ** 2 / 24 * self.alpha ** 2 / (F * self.K) ** (1 - self.beta)
                     + 0.25 * self.rho * self.beta * self.nu * self.alpha / (F * self.K) ** ((1 - self.beta) / 2)
                     + (2 - 3 * self.rho ** 2) * self.nu ** 2 / 24) * self.T

            V = A * z / x_z * B

        return V

    def get_european_option(self):
        """Calcule les prix des options Call et Put européennes en utilisant la volatilité du modèle SABR."""
        vol = self.sabr_volatility()
        d1 = (np.log(self.S / self.K) + (0.5 * vol ** 2) * self.T) / (vol * np.sqrt(self.T))
        d2 = d1 - vol * np.sqrt(self.T)

        # Prix du Call
        call_price = self.S * norm.cdf(d1) - self.K * np.exp(-0.05 * self.T) * norm.cdf(d2)

        # Prix du Put
        put_price = self.K * np.exp(-0.05 * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)

        return call_price, put_price