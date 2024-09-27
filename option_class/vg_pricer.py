import numpy as np

# Modèle Variance Gamma
# Utilisé pour modéliser des sous-jacents où la distribution des rendements présente des queues épaisses et une asymétrie. Le modèle repose sur un processus gamma.
# Particulièrement utilisé dans des marchés avec une distribution des rendements non gaussienne, comme les actions et matières premières.

class VG_pricer:
    def __init__(self, S, K, T, r, sigma, theta, nu, num_simulations=10000):
        self.S = S          # Prix de l'actif sous-jacent
        self.K = K          # Prix d'exercice
        self.T = T          # Maturité
        self.r = r          # Taux sans risque
        self.sigma = sigma  # Volatilité
        self.theta = theta  # Skewness du processus gamma
        self.nu = nu        # Paramètre de variance gamma
        self.num_simulations = num_simulations  # Nombre de simulations Monte Carlo

    def get_european_option(self):
        S_paths = np.zeros(self.num_simulations)
        S_paths.fill(self.S)

        for i in range(self.num_simulations):
            gamma = np.random.gamma(self.T / self.nu, self.nu, 1)
            S_paths[i] *= np.exp((self.r + self.theta) * self.T +
                                 gamma * (self.theta - 0.5 * self.sigma**2) + 
                                 self.sigma * np.random.normal(0, np.sqrt(gamma)))

        call_payoff = np.maximum(S_paths - self.K, 0)
        put_payoff = np.maximum(self.K - S_paths, 0)

        call_price = np.exp(-self.r * self.T) * np.mean(call_payoff)
        put_price = np.exp(-self.r * self.T) * np.mean(put_payoff)

        return call_price, put_price