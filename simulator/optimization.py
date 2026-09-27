import math
import random

from simulator.cost import (
    deployed_capacity,
    determine_deployed_miners
)
from simulator.mining import MinerType
from simulator.scenarios import (
    DeploymentScenario,
    generate_epsilon_scenario
)
from simulator.services import AncillaryService


def calculate_subgradient(
    miners: list[MinerType],
    services: list[AncillaryService],
    c: list[float],
    scenario: DeploymentScenario
) -> list[float]:
    """
    Calcola il subgradiente del costo per uno scenario.

    g_i = r_critical * epsilon_i - p_i
    """

    deployed = deployed_capacity(
        services,
        c,
        scenario.epsilon
    )

    if deployed <= 0:
        return [
            -price
            for price in scenario.service_prices
        ]

    _, critical_type = determine_deployed_miners(
        miners,
        scenario.bitcoin_price,
        scenario.electricity_price,
        deployed
    )

    sorted_miners = sorted(
        miners,
        key=lambda miner: miner.net_reward(
            scenario.bitcoin_price,
            scenario.electricity_price
        )
    )

    r_critical = sorted_miners[critical_type].net_reward(
        scenario.bitcoin_price,
        scenario.electricity_price
    )

    return [
        r_critical * epsilon_i - price
        for epsilon_i, price
        in zip(scenario.epsilon, scenario.service_prices)
    ]


def calculate_stochastic_subgradient(
    miners: list[MinerType],
    services: list[AncillaryService],
    c: list[float],
    scenarios: list[DeploymentScenario]
) -> list[float]:
    """
    Calcola il subgradiente stocastico medio.

    g = (1/M) * sum(g^(m))
    """

    gradients = [
        calculate_subgradient(
            miners,
            services,
            c,
            scenario
        )
        for scenario in scenarios
    ]

    return [
        sum(
            gradient[i]
            for gradient in gradients
        ) / len(gradients)
        for i in range(len(services))
    ]

def project_to_feasible_set(
    c: list[float],
    total_capacity: float
) -> list[float]:
    """
    Proiezione euclidea sull'insieme ammissibile:

        c_i >= 0
        sum(c_i) <= total_capacity
    """

    non_negative = [
        max(value, 0.0)
        for value in c
    ]

    if sum(non_negative) <= total_capacity:
        return non_negative


    sorted_values = sorted(
        non_negative,
        reverse=True
    )

    cumulative_sum = 0.0
    rho = -1

    for i, value in enumerate(sorted_values):

        cumulative_sum += value

        tau_candidate = (
            cumulative_sum - total_capacity
        ) / (i + 1)

        if value - tau_candidate > 0:
            rho = i

    tau = (
        sum(sorted_values[:rho + 1])
        - total_capacity
    ) / (rho + 1)

    return [
        max(value - tau, 0.0)
        for value in non_negative
    ]

def stochastic_subgradient_descent(
    miners: list[MinerType],
    services: list[AncillaryService],
    initial_c: list[float],
    bitcoin_price: float,
    electricity_price: float,
    num_iterations: int = 100,
    num_samples: int = 100,
    price_threshold: float = 60.0,
    reg_up_mean: float = 0.18,
    scenarios: list[DeploymentScenario] | None = None
)-> tuple[
    list[float],
    list[list[float]],
    list[list[float]],
    list[float]
]:
    """
    Implementa lo Stochastic Subgradient Descent
    descritto nell'Algorithm 1 del paper.

    Ad ogni iterazione:

    1. genera M scenari;
    2. calcola il subgradiente medio;
    3. calcola lo step size alpha_j;
    4. aggiorna il profilo;
    5. proietta il profilo nell'insieme ammissibile.

    Restituisce:

    - profilo medio finale;
    - storia dei profili;
    - storia dei subgradienti;
    - storia degli step size.
    """

    c = initial_c.copy()

    history = [c.copy()]
    gradients_history = []
    step_sizes = []

    total_capacity = sum(
        miner.capacity_mw
        for miner in miners
    )

    if len(services) == 1:
        D = total_capacity
    else:
        D = math.sqrt(2) * total_capacity

    for j in range(1, num_iterations + 1):

        if scenarios is None:
            scenarios_j = [
                generate_epsilon_scenario(
                    bitcoin_price=bitcoin_price,
                    electricity_price=electricity_price,
                    threshold=price_threshold,
                    reg_up_mean=reg_up_mean
                )
                for _ in range(num_samples)
            ]
        else:
            scenarios_j = [
                random.choice(scenarios)
                for _ in range(num_samples)
            ]
            

        r_max = max(
            miner.net_reward(
                scenario.bitcoin_price,
                scenario.electricity_price
            )
            for scenario in scenarios_j
            for miner in miners
        )

        p_max = max(
            price
            for scenario in scenarios_j
            for price in scenario.service_prices
        )

        gradient = calculate_stochastic_subgradient(
            miners,
            services,
            c,
            scenarios_j
        )

        alpha = (
            D
            / (
                math.sqrt(len(services))
                * max(r_max, p_max)
                * math.sqrt(j)
            )
        )

        new_c = [
            value - alpha * gradient_value
            for value, gradient_value
            in zip(c, gradient)
        ]

        c = project_to_feasible_set(
            new_c,
            total_capacity
        )

        history.append(c.copy())
        gradients_history.append(gradient)
        step_sizes.append(alpha)

    average_c = [
        sum(
            profile[i]
            for profile in history[:-1]
        ) / num_iterations
        for i in range(len(services))
    ]

    return (
        average_c,
        history,
        gradients_history,
        step_sizes
    )