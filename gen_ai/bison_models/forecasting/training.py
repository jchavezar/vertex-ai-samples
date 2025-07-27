#%%
#region Libraries
from google.cloud import aiplatform as aip
#endregion

#region Variables
project_id="vtxdemos"
region="us-central1"
training_dataset_bq_path="bq://bigquery-public-data:iowa_liquor_sales_forecasting.2020_sales_train"
#endregion


#region Preparing Dataset

# Initialize the AI Platform client.
aip.init(project=project_id, location=region)

dataset = aip.TimeSeriesDataset.create(
    display_name="iowa_liquor_sales_train",
    bq_source=[training_dataset_bq_path],
)

time_column = "date"
time_series_identifier_column = "store_name"
target_column = "sale_dollars"

print(dataset.resource_name)
#%%
column_specs = {
    time_column: "timestamp",
    target_column: "numeric",
    "city": "categorical",
    "zip_code": "categorical",
    "county": "categorical",
}
#endregion

#region Training Pipeline
MODEL_DISPLAY_NAME = "iowa-liquor-sales-forecast-model"

training_job = aip.AutoMLForecastingTrainingJob(
    display_name=MODEL_DISPLAY_NAME,
    optimization_objective="minimize-rmse",
    column_specs=column_specs,
)

model = training_job.run(
    dataset=dataset,
    target_column=target_column,
    time_column=time_column,
    time_series_identifier_column=time_series_identifier_column,
    available_at_forecast_columns=[time_column],
    unavailable_at_forecast_columns=[target_column],
    time_series_attribute_columns=["city", "zip_code", "county"],
    forecast_horizon=30,
    context_window=30,
    data_granularity_unit="day",
    data_granularity_count=1,
    weight_column=None,
    budget_milli_node_hours=1000,
    model_display_name=MODEL_DISPLAY_NAME,
    predefined_split_column_name=None,
)
#endregion
# %%
