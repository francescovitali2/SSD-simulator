import matplotlib.pyplot as plt

from simulator.evaluation import evaluate_profile
from simulator.mining import MinerType
from simulator.scenarios import DeploymentScenario
from simulator.services import AncillaryService


def plot_profile_history(
    history: list[list[float]]
) -> None:
    """
    Mostra l'evoluzione del profilo di partecipazione
    durante le iterazioni SSD.
    """

    iterations = range(len(history))

    price_responsive = [
        profile[0]
        for profile in history
    ]

    reg_up = [
        profile[1]
        for profile in history
    ]

    plt.figure(figsize=(10, 6))

    plt.plot(
        iterations,
        price_responsive,
        label="Price-responsive"
    )

    plt.plot(
        iterations,
        reg_up,
        label="Reg-up"
    )

    plt.xlabel("Iterazione")
    plt.ylabel("Capacità impegnata (MW)")
    plt.title("Evoluzione del profilo SSD")

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def plot_step_sizes(
    step_sizes: list[float]
) -> None:
    """
    Mostra l'andamento dello step size alpha_j
    durante le iterazioni SSD.
    """

    iterations = range(1, len(step_sizes) + 1)

    plt.figure(figsize=(10, 6))

    plt.plot(
        iterations,
        step_sizes,
        label="Alpha"
    )

    plt.xlabel("Iterazione")
    plt.ylabel("Step size α")
    plt.title("Evoluzione dello step size SSD")

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def plot_profit_history(
    history: list[list[float]],
    miners: list[MinerType],
    services: list[AncillaryService],
    scenarios: list[DeploymentScenario],
    reference_profit: float
) -> None:
    """
    Mostra l'evoluzione del profitto associato
    al profilo SSD durante le iterazioni.

    La stessa serie di scenari viene utilizzata
    per tutte le iterazioni, così da rendere
    il confronto coerente.
    """

    iterations = range(len(history))

    profits = [
        evaluate_profile(
            miners=miners,
            services=services,
            profile=profile,
            scenarios=scenarios
        )
        for profile in history
    ]

    plt.figure(figsize=(10, 6))

    plt.plot(
        iterations,
        profits,
        label="SSD"
    )

    plt.axhline(
        y=reference_profit,
        linestyle="--",
        label="Soluzione di riferimento"
    )

    plt.xlabel("Iterazione")
    plt.ylabel("Profitto medio ($)")
    plt.title("Evoluzione del profitto durante SSD")

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()