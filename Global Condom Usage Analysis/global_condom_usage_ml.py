import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

""" If the data shows as '...' then run the below set_option line, otherwise ignore it.
"""
pd.set_option('display.max_columns', None)

#Load Dataset
df = pd.read_csv(r'Rich_Global_Condom_Usage_Dataset.csv')

#Basic Information
print(f'This Dataset contains {df.shape[0]} rows and {df.shape[1]} columns')
round(df.describe(),1)

#ML Predictive Modeling 
non_feature = "Sex Education Programs (Yes/No)"
features = [col for col in df if col != non_feature]
#make copy dataframe of the original dataset to maintain data integrity
ml_df = df.copy()
#encodes each categorical column with numeric value for ML modeling
label_encoders = {}
for col in ml_df.select_dtypes(include=["object"]).columns:
    le = LabelEncoder()
    ml_df[col] = le.fit_transform(ml_df[col])
    label_encoders[col] = le
    
X = ml_df[features]
y = ml_df[non_feature]

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=.2,random_state=33)

#KNN Model
scaler = MinMaxScaler(feature_range=(0,1))
knn_X_train = scaler.fit_transform(X_train)
knn_X_test = scaler.fit_transform(X_test)
knn = KNeighborsClassifier(n_neighbors=8)
knn.fit(knn_X_train,y_train)
knn_y_pred = knn.predict(knn_X_test)
#knn.score(knn_X_test,y_test)

#Logistic Regression
lr = LogisticRegression()
lr.fit(X_train,y_train)
lr_y_pred = lr.predict(X_test)
#lr.score(X_test,y_test)

#Random Forest Classifier
rf = RandomForestClassifier()
rf.fit(X_train,y_train)
rf_y_pred = rf.predict(X_test)
#rf.score(X_test,y_test)

#Random Forest Classifier with Hyperparameter tuning
rf2 = RandomForestClassifier(n_estimators=1000,
                             criterion='entropy',
                             min_samples_split = 10,
                             max_depth=14,
                             random_state=42
                             )
rf2.fit(X_train,y_train)
rf2_y_pred2 = rf2.predict(X_test)
#rf2.score(X_test,y_test)

#Support Vector Machines SVC
svc = SVC()
svc.fit(svc,y_train)
svc_y_pred = svc.predict(X_test)
#svc.score(X_test,y_test)

#Naive Bayes
gb = GaussianNB()
gb.fit(X_train,y_train)
gb_y_pred = gb.predict(X_test)
#gb.score(X_test,y_test)

ml_models = {
    "K-Nearest Neighbors": knn,
    "Logistic Regression": lr,
    "Random Forest Classifier": rf,
    "Random Forest Classifier with Hyperparameter Tuning": rf2,
    "Support Vector Machines (SVC)": svc,
    "Naive Bayes Gaussian":gb
    }

for name, model in ml_models.items():
    if model == knn:
        scaler = MinMaxScaler(feature_range=(0,1))
        knn_X_train = scaler.fit_transform(X_train)
        knn_X_test = scaler.fit_transform(X_test)

        model.fit(knn_X_train,y_train)
        y_pred = model.predict(knn_X_test)
        score = knn.score(knn_X_test,y_test)
    else:
        model.fit(X_train,y_train)
        y_pred = model.predict(X_test)
        score = model.score(X_test,y_test)
    cm = confusion_matrix(y_test,y_pred)
    print(f"{name} is {score:.2%}% accurate!")
    print(f"Confusion Matrix for {name}: \n {cm}")

