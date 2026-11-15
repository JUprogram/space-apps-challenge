from sklearn.ensemble import IsolationForest
import pandas as pd
from inspect_data import analysis_data
print("\n--- IMPORTED COLUMN NAMES ---")
print(analysis_data.columns.tolist())


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
        print("Columns received by prepare_data:")
        print(df.columns.tolist())
        df_clean = df.copy()
        return df_clean.dropna(subset=["Sleep Latency (minutes)", "Sleep Duration (minutes)", "Sleep Efficiency (%)"])



def detect_anomalies(data: pd.DataFrame) -> pd.DataFrame:
	selec = data[["Sleep Latency (minutes)", "Sleep Duration (minutes)", "Sleep Efficiency (%)"]]
	clf = IsolationForest( n_estimators=100, contamination=0.10, random_state=42).fit(selec)
	predictions = clf.predict(selec)

	scores = clf.decision_function(selec)
	results = data.copy()
	results["Predictions"] = predictions
	results["Anomaly Score"] = scores
	
	return results

clean_data = prepare_data(analysis_data)

results = detect_anomalies(clean_data)

print(results[["Predictions", "Anomaly Score"]].head())

X = clean_data[['Sleep Latency (minutes)', 'Sleep Duration (minutes)', 'Sleep Efficiency (%)']]

model = IsolationForest(n_estimators=100, contamination=0.10, random_state=42).fit(X)
predics = model.predict(X)
clean_data["Predictions"] = predics
groupbysub = clean_data.groupby(['Subject'])
negpredics = (clean_data['Predictions'] == -1).groupby(clean_data['Subject']).sum()



conf = model.decision_function(X)
clean_data["Anomaly Score"] = conf

print(clean_data["Anomaly Score"].describe())

clean_data =  analysis_data.dropna(subset=[
        'Sleep Latency (minutes)', 
        'Sleep Duration (minutes)', 
        'Sleep Efficiency (%)' ]).copy()

X = clean_data[['Sleep Latency (minutes)', 'Sleep Duration (minutes)', 'Sleep Efficiency (%)']]

model = IsolationForest(n_estimators=100, contamination=0.10, random_state=42).fit(X)
predics = model.predict(X)
clean_data["Predictions"] = predics
pre = pd.Series(predics)
groupbysub = clean_data.groupby(['Subject'])
negpredics = (clean_data['Predictions'] == -1).groupby(clean_data['Subject']).sum()
predicounts = pre.value_counts().loc[[1,-1]]

conf = model.decision_function(X)
clean_data["Anomaly Score"] = conf

