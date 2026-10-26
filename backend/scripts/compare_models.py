import json
import glob

print("=== NEW CLASSIFICATION MODELS (Trained with 2011) ===")
for f in glob.glob("ml/models/classification_model_202608191416*.json"):
    with open(f) as file:
        data = json.load(file)
        metrics = data["metrics"]
        print(f"Model: {data['model_name']}, F1: {metrics.get('f1', 0):.4f}, Accuracy: {metrics.get('accuracy', 0):.4f}, Log Loss: {metrics.get('log_loss', 'N/A')}")

print("\n=== OLD CLASSIFICATION MODELS (Without 2011) ===")
for f in glob.glob("ml/models/classification_model_202608191401*.json"):
    with open(f) as file:
        data = json.load(file)
        metrics = data["metrics"]
        print(f"Model: {data['model_name']}, F1: {metrics.get('f1', 0):.4f}, Accuracy: {metrics.get('accuracy', 0):.4f}, Log Loss: {metrics.get('log_loss', 'N/A')}")

print("\n=== NEW REGRESSION MODELS ===")
for f in glob.glob("ml/models/regression_model_202608191416*.json"):
    with open(f) as file:
        data = json.load(file)
        metrics = data["metrics"]
        print(f"Model: {data['model_name']}, RMSE: {metrics.get('rmse', 0):.4f}, R2: {metrics.get('r2', 0):.4f}")

print("\n=== OLD REGRESSION MODELS ===")
for f in glob.glob("ml/models/regression_model_202608191401*.json"):
    with open(f) as file:
        data = json.load(file)
        metrics = data["metrics"]
        print(f"Model: {data['model_name']}, RMSE: {metrics.get('rmse', 0):.4f}, R2: {metrics.get('r2', 0):.4f}")
