import pandas as pd
import xgboost as xgb
import numpy as np
import lightgbm as lgb
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error
from sklearn.compose import TransformedTargetRegressor


df = pd.read_csv("datasets/Final_Resale_Data.csv")
df = df.dropna()

# Create Train and Test Set
X = df.drop("Price", axis=1)
y = df["Price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Light GBM
params = {
    "objective": "regression",
    "metric": "rmse",
    "boosting_type": "gbdt",
    "num_leaves": 31,
    "max_depth": 6,
    "learning_rate": 0.1,
    "lambda_l2": 1,
    "min_child_samples": 40,
    "bagging_fraction": 0.8,
    "verbose": -1,
    "random_state": 42
}
num_round = 10000
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

bst = lgb.train(params, train_data, num_round, valid_sets=[test_data], callbacks=[lgb.early_stopping(stopping_rounds=10)])

y_pred = bst.predict(X_test, num_iteration=bst.best_iteration)
train_pred = bst.predict(X_train, num_iterations=bst.best_iteration)
print("Test RMSE:", root_mean_squared_error(y_test, y_pred))
print("Train RMSE:", root_mean_squared_error(y_train, train_pred))



# # Light GBM
# lgbm_model = LGBMRegressor(
#     objective="regression",
#     metric="rmse",
#     num_leaves=100,
#     learning_rate=0.1,
#     n_estimators=500,
#     min_child_samples=20,
#     importance_type="split",
#     feature_fraction=0.8,
#     subsample=0.8,
#     subsample_freq=5,
#     reg_alpha=0.01,
#     reg_lambda=0.01,
#     verbose=-1,
#     random_state=42
# )

# regressor = TransformedTargetRegressor(regressor=lgbm_model,
#                                        func=np.log1p,
#                                        inverse_func=np.expm1)

# regressor.fit(X_train, y_train)
# lgbm_pred = regressor.predict(X_test)
# y_train_pred = regressor.predict(X_train)
# print("Train RMSE:", root_mean_squared_error(y_train, y_train_pred))
# print("Eval RMSE:", root_mean_squared_error(y_test, lgbm_pred))


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