from datetime import datetime, timedelta
import pandas as pd
from dateutil import rrule as rr

from assume import World
from assume.common.market_objects import MarketConfig, MarketProduct
from assume.common.forecasts import NaiveForecast

DB_URI = "sqlite:///assume_db.db"

# ---- time range ----
start = datetime(2023, 10, 4)
end = datetime(2023, 12, 5)
idx = pd.date_range(start=start, end=end + timedelta(hours=24), freq="h")

# ---- world + market ----
world = World(database_uri=DB_URI)
market = [
    MarketConfig(
        "EOM",
        opening_hours=rr.rrule(rr.HOURLY, interval=24, dtstart=start, until=end),
        opening_duration=timedelta(hours=1),
        market_mechanism="pay_as_clear",
        market_products=[MarketProduct(timedelta(hours=1), 24, timedelta(hours=1))],
    )
]

world.setup(start=start, end=end, save_frequency_hours=48, simulation_id="quick_test")
world.add_market_operator(id="mo")
for m in market:
    world.add_market(market_operator_id="mo", market_config=m)

# ---- DEMAND unit (positional args; includes required 'technology')
world.add_unit_operator("demand_op")
world.add_unit(
    "demand",                 # unit_id
    "demand",                 # unit_type
    "demand_op",              # operator_id
    {
        "min_power": 0,
        "max_power": -1000,
        "technology": "demand",
        "bidding_strategies": {"EOM": "elastic_demand"},
    },
    forecaster=NaiveForecast(index=idx, demand=-100),
)

# ---- GENERATOR unit (positional args)
world.add_unit_operator("gen_op")
world.add_unit(
    "plant",                  # unit_id
    "power_plant",            # unit_type
    "gen_op",                 # operator_id
    {
        "min_power": 0,
        "max_power": 1000,
        "technology": "nuclear",
        "bidding_strategies": {"EOM": "naive_eom"},
    },
    forecaster=NaiveForecast(index=idx, availability=1, fuel_price=3, co2_price=0.1),
)

# ---- run ----
world.run()
print("OK — results written to assume_db.db")
