import pandas as pd
import numpy as np
from sklearn.model_selection import(train_test_split,RandomizedSearchCV,TimeSeriesSplit)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from sklearn.metrics import mean_squared_error as ms, mean_absolute_error as mape,r2_score

data=pd.read_csv("Rain_predictor/final_weather_latest.csv")
if data:
  print("Dataset imported")
else:
  print("Check the file location")
data=data.drop(["Unnamed: 0","Unnamed: 0.1","precipitation_sum"],axis=1) #removing unnecessary columns to prevent data leakage and inaccurate training
lat_rad = np.radians(data['latitude'].astype(float))
lon_rad = np.radians(data['longitude'].astype(float))

# Create 3D Cartesian coordinates as brand new features to help model understand georaphical data
data['coord_x'] = np.cos(lat_rad) * np.cos(lon_rad)
data['coord_y'] = np.cos(lat_rad) * np.sin(lon_rad)
data['coord_z'] = np.sin(lat_rad)

print(data)# viewing the data
print(data.columns)
print(data.dtypes)
#-----preprocessing------#
data.isnull().sum() #checking for null
data.duplicated().sum() #checking for duplicates

weather_cols = ["temperature_2m_mean", "relative_humidity_2m_mean", "wind_speed_10m_mean", "wind_gusts_10m_mean"] #clipping outliers to remove noise
count=0
print(" --- CLIPPING SUMMARY REPORT --- \n")
for (lat,lon),city_group in data.groupby(["latitude","longitude"]):
 for col in weather_cols:
    lower_limit = city_group[col].quantile(0.01)
    upper_limit = city_group[col].quantile(0.99)
    

    
    outliers_mask = (city_group[col] < lower_limit) | (city_group[col] > upper_limit)

    clipped_count = outliers_mask.sum()
    total_rows = len(data)
    clipped_percentage = (clipped_count / total_rows) * 100
    count+=clipped_percentage
    
    print(f"🔹 Column: **{col}**")
    print(f"   - Lower Limit (1%): {lower_limit:.2f} | Upper Limit (99%): {upper_limit:.2f}")
    print(f"   - Total rows to be clipped: **{clipped_count}** out of {total_rows}")
    print(f"   - Data impact: **{clipped_percentage:.2f}%**\n")
print(count)


weather_cols = ["temperature_2m_mean", "relative_humidity_2m_mean", "wind_speed_10m_mean", "wind_gusts_10m_mean"]

for (lat, lon), city_group in data.groupby(['latitude', 'longitude']):
    
    for col in weather_cols:
        lower_limit = city_group[col].quantile(0.01)
        upper_limit = city_group[col].quantile(0.99)
        
        row_indices = (data['latitude'] == lat) & (data['longitude'] == lon)
        data.loc[row_indices, col] = data.loc[row_indices, col].clip(lower_limit, upper_limit)

print(" Diverse Dataset Successfully Normalized via Location-Wise Clipping!")

#----feature and target separation-----#
y=data["rain_sum"]
X=data.drop("rain_sum",axis=1)
columns=X.columns

#---creating a pipeline---#
numeric_pipeline=Pipeline(steps=[("scaler",StandardScaler())])
preprocessor=ColumnTransformer(transformers=[("num",numeric_pipeline,columns)])

X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=42,test_size=0.2) #separating training and testing data
model=xgb.XGBRegressor(n_estimators=600,objective="reg:tweedie",eta=0.02,max_depth=8,reg_alpha=5,min_child_weight=2,reg_lambda=3,gamma=0,tweedie_variance_power=1.5,subsample=0.8,colsample_bytree=0.8)# specifying the parameters

final=Pipeline(steps=[("preprocessor",preprocessor),("model",model)]) #final pipeline
final.fit(X_train,y_train) #fitting the model
y_pred= final.predict(X_test)
print(y_pred)#prediciton

#----Evaluation---#
accuracy=ms(y_test,y_pred)
accuracy1=mape(y_test,y_pred)
rscore=r2_score(y_test,y_pred)
print(accuracy,accuracy1,rscore)
