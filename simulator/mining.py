from dataclasses import dataclass


@dataclass
class MinerType:
    name: str
    capacity_mw: float
    energy_intensity: float

    def mining_revenue(self, bitcoin_price: float) -> float:
        """
        Calcola il ricavo del mining per MWh.

        p_b^k = Bitcoin price / Energy intensity
        """
        return bitcoin_price / self.energy_intensity

    def net_reward(
        self,
        bitcoin_price: float,
        electricity_price: float
    ) -> float:
        """
        Calcola il net mining reward:

        r_k = p_b^k - p_e
        """
        return (
            self.mining_revenue(bitcoin_price)
            - electricity_price
        )


class MiningFarm:

    def __init__(self, miners: list[MinerType]):
        self.miners = miners

    @property
    def total_capacity(self) -> float:
        return sum(miner.capacity_mw for miner in self.miners)
