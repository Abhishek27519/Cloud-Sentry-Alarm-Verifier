import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib


# 1. Generate Synthetic Alarm Data
def generate_data():
    np.random.seed(42)

    # Normal Alarms (90% of data)
    normal_data = {
        'duration': np.random.normal(30, 5, 900),  # ~30 seconds
        'severity': np.random.randint(1, 4, 900),  # Low severity 1-3
        'frequency': np.random.normal(2, 0.5, 900)  # Occurs ~2 times/hr
    }

    # False/Anomalous Alarms (10% of data)
    anomalous_data = {
        'duration': np.random.normal(300, 50, 100),  # Unusual long duration
        'severity': np.random.randint(8, 11, 100),  # High severity 8-10
        'frequency': np.random.normal(20, 5, 100)  # Very high frequency
    }

    df_normal = pd.DataFrame(normal_data)
    df_anomalous = pd.DataFrame(anomalous_data)

    df = pd.concat([df_normal, df_anomalous]).sample(frac=1).reset_index(drop=True)
    df.to_csv('alarm_data.csv', index=False)
    print("CSV data generated: alarm_data.csv")
    return df


# 2. Train Isolation Forest
def train_model(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(df)

    # Save the model locally
    joblib.dump(model, 'alarm_model.joblib')
    print("Model trained and saved: alarm_model.joblib")


if __name__ == "__main__":
    data = generate_data()
    train_model(data)