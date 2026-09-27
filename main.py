import random

from simulator.evaluation import evaluate_profile
from simulator.input import SimulationInput, load_hourly_scenarios
from simulator.mining import MinerType, MiningFarm
from simulator.optimization import stochastic_subgradient_descent
from simulator.scenarios import create_scenario_from_data
from simulator.services import AncillaryService

RANDOM_SEED = 42

NUM_ITERATIONS = 100

PRICE_THRESHOLD = 60.0
REG_UP_MEAN = 0.18

random.seed(RANDOM_SEED)
DATA_FILE = "data/experiment_week_april_2020.csv"

hourly_scenarios = load_hourly_scenarios(DATA_FILE)

print(f"Hourly scenarios loaded: {len(hourly_scenarios)}")

experimental_scenarios = [
    create_scenario_from_data(
        bitcoin_price=scenario.bitcoin_price,
        electricity_price=scenario.electricity_price,
        reg_up_epsilon=scenario.reg_up_epsilon,
        price_responsive_price=scenario.price_responsive_price,
        reg_up_price=scenario.reg_up_price,
        threshold=PRICE_THRESHOLD
    )
    for scenario in hourly_scenarios
]

print(
    f"Experimental scenarios created: "
    f"{len(experimental_scenarios)}"
)

efficient = MinerType(
    name="Efficient",
    capacity_mw=100,
    energy_intensity=110
)

less_efficient = MinerType(
    name="Less efficient",
    capacity_mw=150,
    energy_intensity=130
)

farm = MiningFarm([
    efficient,
    less_efficient
])

services = [
    AncillaryService(
        name="Price-responsive",
        price=70
    ),
    AncillaryService(
        name="Reg-up",
        price=50
    )
]

simulation_input = SimulationInput(
    farm=farm,
    bitcoin_price=0,
    electricity_price=0,
    services=services
)

total_capacity = simulation_input.farm.total_capacity

initial_c = [
    total_capacity / len(services)
    for _ in services
]

hourly_profiles = {}

for hour in range(24):

    hour_data = [
        scenario
        for scenario in hourly_scenarios
        if scenario.hour == hour
    ]

    if not hour_data:
        raise ValueError(
            f"Nessun dato disponibile per l'ora {hour:02d}:00"
        )
    hour_scenarios = [
        create_scenario_from_data(
            bitcoin_price=scenario.bitcoin_price,
            electricity_price=scenario.electricity_price,
            reg_up_epsilon=scenario.reg_up_epsilon,
            price_responsive_price=scenario.price_responsive_price,
            reg_up_price=scenario.reg_up_price,
            threshold=PRICE_THRESHOLD
        )
        for scenario in hour_data
    ]

    hour_services = [
        AncillaryService(
            name="Price-responsive",
            price=70.0
        ),
        AncillaryService(
            name="Reg-up",
            price=50.0
        )
    ]

    avg_bitcoin_price = sum(
        scenario.bitcoin_price
        for scenario in hour_data
    ) / len(hour_data)

    avg_electricity_price = sum(
        scenario.electricity_price
        for scenario in hour_data
    ) / len(hour_data)

    hour_initial_c = [
        total_capacity / len(hour_services)
        for _ in hour_services
    ]

    hour_profile, _, _, _ = stochastic_subgradient_descent(
        miners=simulation_input.farm.miners,
        services=hour_services,
        initial_c=hour_initial_c,
        bitcoin_price=avg_bitcoin_price,
        electricity_price=avg_electricity_price,    
        num_iterations=NUM_ITERATIONS,
        num_samples=len(hour_scenarios),
        price_threshold=PRICE_THRESHOLD,
        reg_up_mean=REG_UP_MEAN,
        scenarios=hour_scenarios
    )

    hourly_profiles[hour] = hour_profile


print()
print("PROFILI SSD ORARI")
print("-" * 60)

for hour in range(24):

    profile = hourly_profiles[hour]

    print(
        f"{hour:02d}:00  "
        f"Price-responsive: {profile[0]:7.2f} MW  "
        f"Reg-up: {profile[1]:7.2f} MW"
    )

avg_bitcoin_price = sum(
    scenario.bitcoin_price
    for scenario in hourly_scenarios
) / len(hourly_scenarios)

avg_electricity_price = sum(
    scenario.electricity_price
    for scenario in hourly_scenarios
) / len(hourly_scenarios)

avg_price_responsive = sum(
    scenario.price_responsive_price
    for scenario in hourly_scenarios
) / len(hourly_scenarios)

avg_reg_up = sum(
    scenario.reg_up_price
    for scenario in hourly_scenarios
) / len(hourly_scenarios)

fixed_services = [
    AncillaryService(
        name="Price-responsive",
        price=70.0
    ),
    AncillaryService(
        name="Reg-up",
        price=50.0
    )
]

fixed_scenarios = [
    create_scenario_from_data(
        bitcoin_price=scenario.bitcoin_price,
        electricity_price=scenario.electricity_price,
        reg_up_epsilon=scenario.reg_up_epsilon,
        price_responsive_price=scenario.price_responsive_price,
        reg_up_price=scenario.reg_up_price,
        threshold=PRICE_THRESHOLD
    )
    for scenario in hourly_scenarios
]

fixed_initial_c = [
    total_capacity / len(fixed_services)
    for _ in fixed_services
]

fixed_profile, _, _, _ = stochastic_subgradient_descent(
    miners=simulation_input.farm.miners,
    services=fixed_services,
    initial_c=fixed_initial_c,
    bitcoin_price=avg_bitcoin_price,
    electricity_price=avg_electricity_price,
    num_iterations=NUM_ITERATIONS,
    num_samples=len(fixed_scenarios),
    price_threshold=PRICE_THRESHOLD,
    reg_up_mean=REG_UP_MEAN,
    scenarios=fixed_scenarios
)

fifty_fifty_profile = [
    total_capacity / 2,
    total_capacity / 2
]

print()
print("=" * 60)
print("PROFILI DI PARTECIPAZIONE")
print("=" * 60)

print(
    f"Fixed Profile:"
    f"  Price-responsive = {fixed_profile[0]:.2f} MW |"
    f"  Reg-up = {fixed_profile[1]:.2f} MW"
)

print(
    f"50%-50%:"
    f"          Price-responsive = {fifty_fifty_profile[0]:.2f} MW |"
    f"  Reg-up = {fifty_fifty_profile[1]:.2f} MW"
)

hourly_profits = {
    "SSD": [],
    "Fixed Profile": [],
    "50%-50%": []
}

for hour in range(24):

    hour_data = [
        scenario
        for scenario in hourly_scenarios
        if scenario.hour == hour
    ]

    hour_evaluation_scenarios = [
        create_scenario_from_data(
            bitcoin_price=scenario.bitcoin_price,
            electricity_price=scenario.electricity_price,
            reg_up_epsilon=scenario.reg_up_epsilon,
            price_responsive_price=scenario.price_responsive_price,
            reg_up_price=scenario.reg_up_price,
            threshold=PRICE_THRESHOLD
        )
        for scenario in hour_data
    ]

    ssd_profile = hourly_profiles[hour]

    ssd_profit = evaluate_profile(
        miners=simulation_input.farm.miners,
        services=services,
        profile=ssd_profile,
        scenarios=hour_evaluation_scenarios
    )

    fixed_profit = evaluate_profile(
        miners=simulation_input.farm.miners,
        services=services,
        profile=fixed_profile,
        scenarios=hour_evaluation_scenarios
    )

    fifty_fifty_profit = evaluate_profile(
        miners=simulation_input.farm.miners,
        services=services,
        profile=fifty_fifty_profile,
        scenarios=hour_evaluation_scenarios
    )

    hourly_profits["SSD"].append(ssd_profit)
    hourly_profits["Fixed Profile"].append(fixed_profit)
    hourly_profits["50%-50%"].append(fifty_fifty_profit)


print()
print("=" * 75)
print("PROFITTO MEDIO ORARIO - CONFRONTO DELLE STRATEGIE")
print("=" * 75)

print(
    f"{'Ora':<8}"
    f"{'SSD':>15}"
    f"{'Fixed Profile':>20}"
    f"{'50%-50%':>15}"
)

print("-" * 75)

for hour in range(24):

    print(
        f"{hour:02d}:00"
        f"{hourly_profits['SSD'][hour]:>15.2f}"
        f"{hourly_profits['Fixed Profile'][hour]:>20.2f}"
        f"{hourly_profits['50%-50%'][hour]:>15.2f}"
    )

average_profits = {
    strategy: sum(profits) / len(profits)
    for strategy, profits in hourly_profits.items()
}

ssd_average = average_profits["SSD"]
fixed_average = average_profits["Fixed Profile"]
fifty_fifty_average = average_profits["50%-50%"]

ssd_vs_5050 = (
    (ssd_average - fifty_fifty_average)
    / abs(fifty_fifty_average)
    * 100
)

ssd_vs_fixed = (
    (ssd_average - fixed_average)
    / abs(fixed_average)
    * 100
)

print()
print("=" * 60)
print("RISULTATI SPERIMENTALI")
print("=" * 60)

print(
    f"SSD:             {ssd_average:10.2f} $"
)

print(
    f"Fixed Profile:   {fixed_average:10.2f} $"
)

print(
    f"50%-50%:         {fifty_fifty_average:10.2f} $"
)

print()

print(
    f"SSD vs 50%-50%:  {ssd_vs_5050:+.2f}%"
)

print(
    f"SSD vs Fixed:    {ssd_vs_fixed:+.2f}%"
)

print("=" * 60)

import matplotlib.pyplot as plt

hours = list(range(24))

plt.figure(figsize=(12, 6))

plt.plot(
    hours,
    hourly_profits["SSD"],
    marker="o",
    label="SSD"
)

plt.plot(
    hours,
    hourly_profits["Fixed Profile"],
    marker="s",
    label="Fixed Profile"
)

plt.plot(
    hours,
    hourly_profits["50%-50%"],
    marker="^",
    label="50%-50%"
)

plt.xlabel("Hour of the day")
plt.ylabel("Average profit ($)")
plt.title("Average Hourly Profit - Comparison of Participation Strategies")

plt.xticks(hours)

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()

plt.savefig(
    "hourly_profit_comparison.png",
    dpi=300
)

plt.show()

print()
print("=" * 70)
print("ESPERIMENTO DI CONVERGENZA SSD")
print("=" * 70)

avg_bitcoin_price = sum(
    scenario.bitcoin_price
    for scenario in experimental_scenarios
) / len(experimental_scenarios)

avg_electricity_price = sum(
    scenario.electricity_price
    for scenario in experimental_scenarios
) / len(experimental_scenarios)

iteration_values = [10, 25, 50, 100, 200, 500]

for iterations in iteration_values:

    convergence_profile, _, _, _ = stochastic_subgradient_descent(
        miners=simulation_input.farm.miners,
        services=services,
        initial_c=initial_c,
        bitcoin_price=avg_bitcoin_price,
        electricity_price=avg_electricity_price,
        num_iterations=iterations,
        num_samples=100,
        price_threshold=PRICE_THRESHOLD,
        reg_up_mean=REG_UP_MEAN,
        scenarios=experimental_scenarios
    )

    profit = evaluate_profile(
        miners=simulation_input.farm.miners,
        services=services,
        profile=convergence_profile,
        scenarios=experimental_scenarios
    )

    print(
        f"J = {iterations:3d} | "
        f"Price-responsive = {convergence_profile[0]:7.2f} MW | "
        f"Reg-up = {convergence_profile[1]:7.2f} MW | "
        f"Profit = {profit:10.2f} $"
    )