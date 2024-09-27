import numpy as np

# Modèle Binomial
# Utilisé pour évaluer les options en construisant un arbre binomial où le prix du sous-jacent évolue de manière discrète.
# Particulièrement utile pour les options américaines ou européennes, car il permet de modéliser l'exercice anticipé (pour les options américaines).
# La précision augmente avec le nombre d'étapes dans l'arbre.

class Binomial_pricer:
    def __init__(self, S, K, T, r, sigma, steps):
        self.S = S           # Prix de l'actif sous-jacent
        self.K = K           # Prix d'exercice
        self.T = T           # Maturité
        self.r = r           # Taux sans risque
        self.sigma = sigma   # Volatilité
        self.steps = steps   # Nombre d'étapes dans l'arbre binomial
        self.dt = T / steps  # Taille d'un intervalle de temps
        self.u = np.exp(sigma * np.sqrt(self.dt))  # Facteur de hausse
        self.d = 1 / self.u  # Facteur de baisse
        self.q = (np.exp(r * self.dt) - self.d) / (self.u - self.d)  # Probabilité de montée

    def price_option(self, option_type="call"):
        stock_price = np.zeros(self.steps + 1)
        call_price = np.zeros(self.steps + 1)
        put_price = np.zeros(self.steps + 1)

        for i in range(self.steps + 1):
            stock_price[i] = self.S * (self.u ** (self.steps - i)) * (self.d ** i)
            call_price[i] = max(0, stock_price[i] - self.K)
            put_price[i] = max(0, self.K - stock_price[i])
        
        # Calcul du prix des options en remontant l'arbre
        for step in range(self.steps - 1, -1, -1):
            for i in range(step + 1):
                call_price[i] = np.exp(-self.r * self.dt) * (self.q * call_price[i] + (1 - self.q) * call_price[i + 1])
                put_price[i] = np.exp(-self.r * self.dt) * (self.q * put_price[i] + (1 - self.q) * put_price[i + 1])

        return call_price[0], put_price[0]