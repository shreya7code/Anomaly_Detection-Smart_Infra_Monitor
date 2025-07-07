import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import joblib


#read from csv
df = pd.read_csv("training_data_InfluxDB_metrics.csv")


#csv cleanup - keepiing the desired columns
df_clean = df[["timestamp", "cpu", "memory", "disk"]].copy()

#converting timestamp to datetime
df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp"])

print(f"df.clean after rename-timestamp: \n {df_clean.head()}")

# dataframe for modelling, without timestamp
df2 = df_clean[["cpu", "memory", "disk"]]


#training the anomaly detector
#creating Isolation Forest model
# assuming 5% data as anomalies 
model = IsolationForest(contamination = 0.05, random_state = 42)

#midel fitting
model.fit(df2)

#predicting anomalies
df_clean["anomaly"] = model.predict(df2)

# Converting prediction to 1 for anomaly (outlier), 0 for normal
df_clean["anomaly"] = df_clean["anomaly"].apply(lambda x: 1 if x==-1 else 0)

print(f"df.clean after anomaly prediction: \n {df_clean.head()}")

#now filtering all anomalies
anomalies = df_clean[df_clean["anomaly"] == 1]

#visualizing the results
plt.figure(figsize=(12,5))
plt.plot(df_clean["timestamp"], df_clean["cpu"], label="CPU usage")
plt.scatter(anomalies["timestamp"], anomalies["cpu"],
            color = "red", marker="x", label = "Anomaly")

plt.title("CPU Usage and Detected Anomalies")
plt.xlabel("Timestamp")
plt.ylabel("CPU Usage (%)")

# Save to file
plt.savefig("cpu_anomalies_plot.png", dpi=300, bbox_inches='tight')

plt.show()

#Saving the model in local
joblib.dump(model, "isolation_forest_model.pkl")

#print all anomalies
print("df.clean after model run; for anomaly=1 : \n", df_clean[df_clean["anomaly"] == 1])


