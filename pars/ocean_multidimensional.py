import os
from dotenv import load_dotenv
from beacon_api import Client

load_dotenv()
EMAIL = os.getenv("EMAIL")

client = Client("https://beacon-wod.maris.nl",
                user_agent=f"my-app/1.0 ({EMAIL})")

available_tables = client.list_tables()
query_builder = available_tables["default"].query()

query_builder.add_select_column("wod_unique_cast")
query_builder.add_select_column("Platform", alias="PLATFORM")
query_builder.add_select_column("Institute", alias="INSTITUTE")
query_builder.add_select_column("Temperature", alias="TEMPERATURE")
query_builder.add_select_column("Temperature_WODflag", alias="TEMPERATURE_QC")
query_builder.add_select_column("Temperature.units", alias="TEMPERATURE_UNIT")
query_builder.add_select_column("z", alias="DEPTH")
query_builder.add_select_column("z.units", alias="DEPTH_UNIT")
query_builder.add_select_column("time", alias="TIME")
query_builder.add_select_column("lon", alias="LONGITUDE")
query_builder.add_select_column("lat", alias="LATITUDE")
query_builder.add_select_column(".featureType", alias="FEATURE_TYPE")

query_builder.add_range_filter("TIME", "2022-01-01T00:00:00", "2023-01-01T00:00:00")
query_builder.add_is_not_null_filter("TEMPERATURE")
query_builder.add_not_equals_filter("TEMPERATURE", -1e+10)
query_builder.add_equals_filter("TEMPERATURE_QC", 0.0)
query_builder.add_range_filter("DEPTH", 0, 10)

df = query_builder.to_pandas_dataframe().sort_values(by="TIME", ascending=False).iloc[0:1500,]
df.to_csv("data/wod.csv")