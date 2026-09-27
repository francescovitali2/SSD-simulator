from dataclasses import dataclass
import random


@dataclass
class DeploymentScenario:
    """
    Rappresenta uno scenario di deployment dei servizi
    ancillari per una determinata condizione di mercato.
    """

    bitcoin_price: float
    electricity_price: float
    epsilon: list[float]
    service_prices: list[float]


def generate_price_responsive_epsilon(
    electricity_price: float,
    threshold: float = 60.0
) -> float:
    """
    Genera il deployment rate del servizio Price-responsive.

    Semplificazione adottata nel dimostratore:

        epsilon = 1  se electricity_price > threshold
        epsilon = 0  altrimenti
    """

    return 1.0 if electricity_price > threshold else 0.0


def generate_reg_up_epsilon(
    mean: float = 0.18
) -> float:
    """
    Genera il deployment rate del servizio Reg-up.

    Semplificazione adottata nel dimostratore:
    il deployment rate segue una distribuzione esponenziale
    con media pari a 'mean'.

    Il valore viene limitato all'intervallo [0, 1].
    """

    if mean <= 0:
        raise ValueError("La media deve essere maggiore di zero.")

    lambd = 1.0 / mean

    epsilon = random.expovariate(lambd)

    return min(epsilon, 1.0)


def generate_epsilon_scenario(
    bitcoin_price: float,
    electricity_price: float,
    threshold: float = 60.0,
    reg_up_mean: float = 0.18
) -> DeploymentScenario:
    """
    Genera uno scenario di deployment.

    Il prezzo del Bitcoin e il prezzo dell'elettricità
    sono input dello scenario.

    L'SSD non campiona i prezzi di mercato:
    campiona solamente i deployment rate epsilon.

    Servizi considerati:

    1. Price-responsive
       epsilon = 1 se electricity_price > threshold,
       epsilon = 0 altrimenti.

    2. Reg-up
       epsilon generato da una distribuzione esponenziale
       con media reg_up_mean.
    """

    epsilon_price = generate_price_responsive_epsilon(
        electricity_price=electricity_price,
        threshold=threshold
    )

    epsilon_reg_up = generate_reg_up_epsilon(
        mean=reg_up_mean
    )

    return DeploymentScenario(
        bitcoin_price=bitcoin_price,
        electricity_price=electricity_price,
        epsilon=[
            epsilon_price,
            epsilon_reg_up
        ],
        service_prices=[
            70.0,
            50.0
        ]
    )

def create_scenario_from_data(
    bitcoin_price: float,
    electricity_price: float,
    reg_up_epsilon: float,
    price_responsive_price: float,
    reg_up_price: float,
    threshold: float = 60.0
) -> DeploymentScenario:
    """
    Crea uno scenario di deployment a partire
    dai dati del dataset sperimentale.
    """

    epsilon_price = generate_price_responsive_epsilon(
        electricity_price=electricity_price,
        threshold=threshold
    )

    return DeploymentScenario(
        bitcoin_price=bitcoin_price,
        electricity_price=electricity_price,
        epsilon=[
            epsilon_price,
            reg_up_epsilon
        ],
        service_prices=[
            price_responsive_price,
            reg_up_price
        ]
    )