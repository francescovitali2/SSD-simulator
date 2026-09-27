from simulator.mining import MinerType
from simulator.services import AncillaryService


def deployed_capacity(
    services: list[AncillaryService],
    c: list[float],
    epsilon: list[float]
) -> float:
    """
    Calcola la capacità effettivamente dispiegata.

    D = sum(epsilon_i * c_i)
    """

    return sum(
        epsilon_i * c_i
        for c_i, epsilon_i in zip(c, epsilon)
    )


def determine_deployed_miners(
    miners: list[MinerType],
    bitcoin_price: float,
    electricity_price: float,
    deployed: float
) -> tuple[list[float], int]:
    """
    Determina quali tipi di miner vengono utilizzati
    per fornire la capacità dispiegata.

    I miner vengono utilizzati in ordine crescente
    di net mining reward.

    Restituisce:
        d_k = capacità dispiegata per ogni tipo
        k_c = indice del critical type

    Se deployed = 0, non viene utilizzato alcun miner
    e critical_type = -1.
    """

    sorted_miners = sorted(
        miners,
        key=lambda miner: miner.net_reward(
            bitcoin_price,
            electricity_price
        )
    )

    remaining = deployed
    d = [0.0] * len(sorted_miners)
    critical_type = -1

    if deployed <= 0:
        return [0.0] * len(sorted_miners), -1

    for k, miner in enumerate(sorted_miners):

        if remaining <= 0:
            break

        deployed_from_miner = min(
            remaining,
            miner.capacity_mw
        )

        d[k] = deployed_from_miner

        remaining -= deployed_from_miner

        if deployed_from_miner < miner.capacity_mw:
            critical_type = k
            break

        if remaining <= 0:
            critical_type = k

    return d, critical_type


def calculate_cost(
    miners: list[MinerType],
    services: list[AncillaryService],
    c: list[float],
    epsilon: list[float],
    bitcoin_price: float,
    electricity_price: float
) -> float:
    """
    Calcola il costo della soluzione:

    cost = lost mining revenue - ancillary service revenue
    """

    deployed = deployed_capacity(
        services,
        c,
        epsilon
    )

    d, critical_type = determine_deployed_miners(
        miners,
        bitcoin_price,
        electricity_price,
        deployed
    )

    if critical_type == -1:

        ancillary_revenue = sum(
            service.price * c_i
            for service, c_i
            in zip(services, c)
        )

        return -ancillary_revenue

    sorted_miners = sorted(
        miners,
        key=lambda miner: miner.net_reward(
            bitcoin_price,
            electricity_price
        )
    )

    lost_mining_revenue = sum(
        miner.net_reward(
            bitcoin_price,
            electricity_price
        ) * deployed_capacity_for_miner
        for miner, deployed_capacity_for_miner
        in zip(sorted_miners, d)
    )

    ancillary_revenue = sum(
        service.price * c_i
        for service, c_i
        in zip(services, c)
    )

    return lost_mining_revenue - ancillary_revenue