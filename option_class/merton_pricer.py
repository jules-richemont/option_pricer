import numpy as np
from scipy.stats import norm

# Modèle de Merton
# Utilisé pour capturer les sauts soudains dans le prix d'un actif, en modélisant un processus de saut en plus du mouvement brownien.
# Particulièrement utile pour des sous-jacents qui peuvent subir des chocs brusques et rares, tels que des annonces économiques.

class Merton_pricer:
    def __init__(self, S, K, T, r, sigma, lambda_j, mu_j, sigma_j, num_simulations=10000):
        self.S = S          # Prix de l'actif sous-jacent
        self.K = K          # Prix d'exercice
        self.T = T          # Maturité
        self.r = r          # Taux sans risque
        self.sigma = sigma  # Volatilité du sous-jacent
        self.lambda_j = lambda_j  # Taux d'arrivée des sauts (Poisson)
        self.mu_j = mu_j    # Taille moyenne des sauts (log-normale)
        self.sigma_j = sigma_j  # Volatilité des sauts
        self.num_simulations = num_simulations  # Nombre de simulations Monte Carlo

    def get_european_option(self):
        dt = self.T / 365
        S_paths = np.zeros(self.num_simulations)
        S_paths.fill(self.S)

        for i in range(self.num_simulations):
            N = np.random.poisson(self.lambda_j * self.T)  # Nombre de sauts
            jump_sizes = np.random.normal(self.mu_j, self.sigma_j, N)  # Taille des sauts
            S_jumps = np.exp(np.sum(jump_sizes))  # Facteur multiplicatif dû aux sauts
            S_paths[i] *= S_jumps * np.exp((self.r - 0.5 * self.sigma**2) * self.T +
                                           self.sigma * np.sqrt(self.T) * np.random.normal())

        call_payoff = np.maximum(S_paths - self.K, 0)
        put_payoff = np.maximum(self.K - S_paths, 0)

        call_price = np.exp(-self.r * self.T) * np.mean(call_payoff)
        put_price = np.exp(-self.r * self.T) * np.mean(put_payoff)

        return call_price, put_price