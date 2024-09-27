import numpy as np
from scipy.stats import norm

# Modèle de Heston (Volatilité Stochastique)
# Utilisé pour modéliser des options où la volatilité du sous-jacent n'est pas constante, mais évolue selon un processus stochastique.
# Il est particulièrement adapté aux marchés où la volatilité fluctue fortement dans le temps.
# Modèle populaire pour capturer des phénomènes comme le "smile" de volatilité observé sur les marchés.

class Heston_pricer:
    def __init__(self, S, K, T, r, kappa, theta, xi, rho, v0, mu, num_simulations=10000, num_steps=100):
        self.S = S                   # Prix actuel du sous-jacent
        self.K = K                   # Prix d'exercice
        self.T = T                   # Maturité
        self.r = r                   # Taux sans risque
        self.kappa = kappa           # Vitesse de réversion de la variance vers theta
        self.theta = theta           # Variance à long terme
        self.xi = xi                 # Volatilité de la variance (vol de vol)
        self.rho = rho               # Corrélation entre les processus de prix et de variance
        self.v0 = v0                 # Variance initiale
        self.mu = mu                 # Taux de rendement du sous-jacent
        self.num_simulations = num_simulations  # Nombre de simulations Monte Carlo
        self.num_steps = num_steps   # Nombre de pas dans chaque simulation

    def simulate_paths(self):
        """Simule les chemins du modèle Heston pour le sous-jacent et la volatilité."""
        dt = self.T / self.num_steps
        S_paths = np.zeros((self.num_steps + 1, self.num_simulations))
        v_paths = np.zeros((self.num_steps + 1, self.num_simulations))
        
        # Conditions initiales
        S_paths[0] = self.S
        v_paths[0] = self.v0
        
        # Générer des variables aléatoires corrélées
        Z1 = np.random.randn(self.num_steps, self.num_simulations)
        Z2 = np.random.randn(self.num_steps, self.num_simulations)
        W1 = Z1
        W2 = self.rho * Z1 + np.sqrt(1 - self.rho ** 2) * Z2
        
        for t in range(1, self.num_steps + 1):
            # Simulation des chemins pour la variance (Heston)
            v_paths[t] = np.abs(v_paths[t - 1] + self.kappa * (self.theta - v_paths[t - 1]) * dt +
                                self.xi * np.sqrt(v_paths[t - 1] * dt) * W2[t - 1])
            
            # Simulation des chemins pour le sous-jacent
            S_paths[t] = S_paths[t - 1] * np.exp((self.mu - 0.5 * v_paths[t - 1]) * dt +
                                                 np.sqrt(v_paths[t - 1] * dt) * W1[t - 1])

        return S_paths

    def get_european_option(self):
        """Calcule les prix des options Call et Put européennes en utilisant le modèle de Heston."""
        S_paths = self.simulate_paths()
        # Calculer les prix à maturité
        S_T = S_paths[-1]
        call_payoff = np.maximum(S_T - self.K, 0)
        put_payoff = np.maximum(self.K - S_T, 0)

        # Actualisation pour obtenir les prix
        call_price = np.exp(-self.r * self.T) * np.mean(call_payoff)
        put_price = np.exp(-self.r * self.T) * np.mean(put_payoff)

        return call_price, put_price