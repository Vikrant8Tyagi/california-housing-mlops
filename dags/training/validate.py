import mlflow
import mlflow.sklearn
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

THRESHOLD_MSE = 1.0

def validate_and_register():
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("california-housing")

    client = mlflow.tracking.MlflowClient()

    experiment = client.get_experiment_by_name("california-housing")
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.mse ASC"],
        max_results=1,
    )

    best_run = runs[0]
    mse = best_run.data.metrics["mse"]
    run_id = best_run.info.run_id

    print(f"Best MSE: {mse}")

    if mse <= THRESHOLD_MSE:
        model_uri = f"runs:/{run_id}/model"
        result = mlflow.register_model(
            model_uri=model_uri,
            name="CaliforniaHousingModel",
        )

        client.transition_model_version_stage(
            name="CaliforniaHousingModel",
            version=result.version,
            stage="Production",
            archive_existing_versions=True,
        )

        print("✅ Model promoted to Production")
    else:
        raise ValueError("❌ Model failed validation")
