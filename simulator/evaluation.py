from simulator.cost import calculate_cost
from simulator.services import AncillaryService


def evaluate_profile(miners, services, profile, scenarios):
    """
    Valuta un profilo di partecipazione su una serie di scenari.

    Per ogni scenario vengono utilizzati:
    - prezzo Bitcoin dello scenario
    - prezzo dell'elettricità dello scenario
    - epsilon dello scenario
    - prezzi dei servizi dello scenario

    Restituisce il profitto medio.
    """

    if not scenarios:
        raise ValueError("La lista degli scenari non può essere vuota.")

    total_profit = 0.0

    for scenario in scenarios:

        scenario_services = [
            AncillaryService(
                name=service.name,
                price=price
            )
            for service, price in zip(services, scenario.service_prices)
        ]

        cost = calculate_cost(
            miners=miners,
            services=scenario_services,
            c=profile,
            epsilon=scenario.epsilon,
            bitcoin_price=scenario.bitcoin_price,
            electricity_price=scenario.electricity_price
        )

        total_profit -= cost

    return total_profit / len(scenarios)