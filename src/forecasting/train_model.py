
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("Loading training and testing datasets...")

train_df = pd.read_parquet(
    "data/processed/train_data.parquet"
)

test_df = pd.read_parquet(
    "data/processed/test_data.parquet"
)

# Features used by the model
features = [
    "store_id",
    "product_id",
    "day_of_week",
    "month",
    "is_weekend",
    "holiday_flag",
    "discount",
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_mean_7"
]

target = "demand"

# Use a manageable sample for the first experiment
train_sample = train_df.sample(
    n=min(300000, len(train_df)),
    random_state=42
)

X_train = train_sample[features]
y_train = train_sample[target]

X_test = test_df[features]
y_test = test_df[target]

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

print("\nTraining Random Forest model...")

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("\nModel training completed!")

print("\nMaking predictions...")

predictions = model.predict(X_test)

# Model evaluation
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

print("\n========== MODEL EVALUATION ==========")
print("MAE:", round(mae, 4))
print("RMSE:", round(rmse, 4))
print("R2 Score:", round(r2, 4))

# Save model
Path("models").mkdir(exist_ok=True)

joblib.dump(
    {"model": model, "features": features},
    "models/demand_forecasting_model.pkl"
)

print("\nModel saved successfully!")
