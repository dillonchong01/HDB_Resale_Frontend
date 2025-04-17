import pandas as pd
import xgboost as xgb
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error, r2_score

df = pd.read_csv("datasets/Final_Resale_Data.csv")
df = df.dropna()

# Create Train and Test Set
X = df.drop("Price", axis=1)
y = df["Price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Light GBM
lgbm_model = LGBMRegressor(
    objective="regression",
    metric="rmse",
    num_leaves=127,
    learning_rate=0.1,
    verbose=-1,
    random_state=42)

lgbm_model.fit(X_train, y_train)
lgbm_pred = lgbm_model.predict(X_test)
y_train_pred = lgbm_model.predict(X_train)
print("Train RMSE:", root_mean_squared_error(y_train, y_train_pred))
print("Eval RMSE:", root_mean_squared_error(y_test, lgbm_pred))


# # Random Forest
# rf_model = RandomForestRegressor(random_state=42)
# rf_model.fit(X_train, y_train)
# rf_pred = rf_model.predict(X_test)
# print("RandomForest RMSE:", root_mean_squared_error(y_test, rf_pred))
# print("RandomForest R²:", r2_score(y_test, rf_pred))

# # XGBoost
# xgb_model = xgb.XGBRegressor(random_state=42)
# xgb_model.fit(X_train, y_train)
# xgb_pred = xgb_model.predict(X_test)
# print("XGBoost RMSE:", root_mean_squared_error(y_test, xgb_pred))
# print("XGBoost R²:", r2_score(y_test, xgb_pred))