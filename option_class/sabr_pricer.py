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
        if alpha <= 0:
            raise ValueError("Alpha must be positive")
        self.alpha = alpha  # Volatilité initiale
        if not (0 <= beta <= 1):
            raise ValueError("Beta must be between 0 and 1")
        self.beta = beta    # Paramètre de forme (0 <= beta <= 1)
        if not (-1 <= rho <= 1):
            raise ValueError("Rho must be between -1 and 1")
        self.rho = rho      # Corrélation entre les processus de volatilité et de prix
        if nu <= 0:
            raise ValueError("Nu must be positive")
        self.nu = nu        # Volatilité de la volatilité

    def sabr_volatility(self):
        F = self.S
        K = self.K

        if F <= 0 or K <= 0:
            raise ValueError("F and K must be positive")

        if F == K:
            # Cas où K est égal à F (Prix forward)
            term1 = ((1 - self.beta) ** 2 / 24) * (self.alpha ** 2 / F ** (2 - 2 * self.beta)) * self.T
            term2 = (self.rho * self.beta * self.nu * self.alpha) / (4 * F ** (1 - self.beta)) * self.T
            term3 = (2 - 3 * self.rho ** 2) * (self.nu ** 2 / 24) * self.T
            V = self.alpha * (1 + term1 + term2 + term3)
        else:
            logFK = np.log(F / K)
            FK_beta = (F * K) ** ((1 - self.beta) / 2)
            z = (self.nu / self.alpha) * FK_beta * logFK
            x_z_numerator = np.sqrt(1 - 2 * self.rho * z + z ** 2) + z - self.rho
            x_z_denominator = 1 - self.rho
            if x_z_denominator == 0 or x_z_numerator <= 0:
                raise ValueError("Invalid parameters leading to division by zero or logarithm of non-positive number in x_z calculation.")
            x_z = np.log(x_z_numerator / x_z_denominator)

            A = self.alpha / (FK_beta * (1 + ((1 - self.beta) ** 2 / 24) * logFK ** 2
                                         + ((1 - self.beta) ** 4 / 1920) * logFK ** 4))

            B = 1 + (((1 - self.beta) ** 2 / 24) * (self.alpha ** 2) / (F * K) ** (1 - self.beta)
                     + 0.25 * self.rho * self.beta * self.nu * self.alpha / FK_beta
                     + (2 - 3 * self.rho ** 2) * (self.nu ** 2 / 24)) * self.T

            if x_z == 0:
                raise ValueError("x_z equals zero, leading to division by zero in volatility calculation.")

            V = A * z / x_z * B

        return V

    def get_european_option(self):
        vol = self.sabr_volatility()
        if vol <= 0:
            raise ValueError("Calculated volatility is non-positive.")
        d1 = (np.log(self.S / self.K) + (0.5 * vol ** 2) * self.T) / (vol * np.sqrt(self.T))
        d2 = d1 - vol * np.sqrt(self.T)

        call_price = self.S * norm.cdf(d1) - self.K * np.exp(-0.05 * self.T) * norm.cdf(d2)
        put_price = self.K * np.exp(-0.05 * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)

        return call_price, put_price