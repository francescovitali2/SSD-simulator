from dataclasses import dataclass

from simulator.mining import MiningFarm
from simulator.services import AncillaryService


@dataclass
class HourlyScenario:
    """
    Dati di mercato relativi a una singola ora
    dell'esperimento.
    """

    date: str
    hour: int

    electricity_price: float
    bitcoin_price: float

    price_responsive_price: float
    reg_up_price: float

    reg_up_epsilon: float


@dataclass
class SimulationInput:
    """
    Contiene gli input del problema di simulazione
    per una singola configurazione di mercato.
    """

    farm: MiningFarm

    bitcoin_price: float

    electricity_price: float

    services: list[AncillaryService]

import csv
from pathlib import Path


def load_hourly_scenarios(
    file_path: str | Path
) -> list[HourlyScenario]:
    """
    Carica gli scenari orari dal dataset CSV.
    """

    scenarios = []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            scenarios.append(
                HourlyScenario(
                    date=row["date"],
                    hour=int(row["hour"]),
                    electricity_price=float(row["electricity_price"]),
                    bitcoin_price=float(row["bitcoin_price"]),
                    price_responsive_price=float(
                        row["price_responsive_price"]
                    ),
                    reg_up_price=float(row["reg_up_price"]),
                    reg_up_epsilon=float(row["reg_up_epsilon"]),
                )
            )

    return scenarios