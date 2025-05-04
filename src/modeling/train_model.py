import pandas as pd
import numpy as np
import os
import yaml
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import joblib
import tempfile

DATA_PATH = "data/processed/model_ready_dataset.csv"
PARAMS_PATH = ".config/params.yaml"

# Load params.yaml
with open(PARAMS_PATH, "r") as f:
    params = yaml.safe_load(f)

def load_data(data_path, target_column, test_size, random_state):
    df = pd.read_csv(data_path)
    X = df.drop(target_column, axis=1)
    y = df[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def evaluate_model(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return mae, rmse

def train_and_log_model(model_name, model_class, param_dist):
    X_train, X_test, y_train, y_test = load_data(
        DATA_PATH,
        target_column=params['model']['target_column'],
        test_size=params['train']['test_size'],
        random_state=params['train']['random_state']
    )

    search = RandomizedSearchCV(
        model_class(),
        param_distributions=param_dist,
        n_iter=params['train']['n_iter_search'],
        cv=params['train']['cv_folds'],
        verbose=1,
        n_jobs=-1,
        random_state=params['train']['random_state']
    )
    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test)
    mae, rmse = evaluate_model(y_test, y_pred)

    with mlflow.start_run(run_name=f"{model_name}_experiment") as run:
        mlflow.log_param("model_type", model_name)
        mlflow.log_params(search.best_params_)
        mlflow.log_metric("MAE", mae)
        mlflow.log_metric("RMSE", rmse)

        # Save & log model artifact
        with tempfile.TemporaryDirectory() as tmp_dir:
            model_path = os.path.join(tmp_dir, "best_model.pkl")
            joblib.dump(best_model, model_path)
            mlflow.log_artifact(model_path, artifact_path="model")

        print(f"[+] {model_name} Best MAE: {mae:.4f}, RMSE: {rmse:.4f}")

        os.makedirs("models", exist_ok=True)
        joblib.dump(best_model, "models/best_model.pkl")


if __name__ == "__main__":
    mlflow.set_tracking_uri(params['model']['tracking_uri'])
    mlflow.set_experiment(params['model']['experiment_name'])

    xgb_param_dist = {
        "n_estimators": params['xgboost']['n_estimators'],
        "learning_rate": params['xgboost']['learning_rate'],
        "max_depth": params['xgboost']['max_depth'],
        "subsample": params['xgboost']['subsample'],
        "colsample_bytree": params['xgboost']['colsample_bytree']
    }

    lgbm_param_dist = {
        "n_estimators": params['lightgbm']['n_estimators'],
        "learning_rate": params['lightgbm']['learning_rate'],
        "num_leaves": params['lightgbm']['num_leaves'],
        "min_child_samples": params['lightgbm']['min_child_samples'],
        "subsample": params['lightgbm']['subsample']
    }

    print("[*] Training XGBoost...")
    train_and_log_model("XGBoost", XGBRegressor, xgb_param_dist)

    print("[*] Training LightGBM...")
    train_and_log_model("LightGBM", LGBMRegressor, lgbm_param_dist)
