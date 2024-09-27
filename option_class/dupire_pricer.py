import numpy as np
from scipy.interpolate import interp2d

# Modèle de Local Volatility (Dupire)
# Utilisé pour ajuster la surface de volatilité implicite observée sur le marché. La volatilité est modélisée comme une fonction du sous-jacent et du temps.
# Utilisé pour des options exotiques ou pour modéliser la dynamique de volatilité en fonction du prix et du temps.

class Dupire_pricer:
    def __init__(self, S, K, T, r, local_vol_surface, num_simulations=10000, num_steps=100):
        self.S = S  # Prix de l'actif sous-jacent
        self.K = K  # Prix d'exercice
        self.T = T  # Maturité
        self.r = r  # Taux sans risque
        self.local_vol_surface = local_vol_surface  # Surface de volatilité locale
        self.num_simulations = num_simulations  # Nombre de simulations Monte Carlo
        self.num_steps = num_steps  # Nombre de pas dans les simulations

    def local_vol(self, S, t):
        return self.local_vol_surface(S, t)  # Utilise la surface de volatilité locale

    def get_european_option(self):
        dt = self.T / self.num_steps
        S_paths = np.zeros((self.num_steps + 1, self.num_simulations))
        S_paths[0] = self.S

        for t in range(1, self.num_steps + 1):
            for i in range(self.num_simulations):
                vol = self.local_vol(S_paths[t - 1, i], t * dt)
                dW = np.random.normal(0, np.sqrt(dt))
                S_paths[t, i] = S_paths[t - 1, i] * np.exp((self.r - 0.5 * vol**2) * dt + vol * dW)

        S_T = S_paths[-1]
        call_payoff = np.maximum(S_T - self.K, 0)
        put_payoff = np.maximum(self.K - S_T, 0)

        call_price = np.exp(-self.r * self.T) * np.mean(call_payoff)
        put_price = np.exp(-self.r * self.T) * np.mean(put_payoff)

        return call_price, put_price