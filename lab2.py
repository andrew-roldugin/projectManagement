import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pandas import DataFrame
from pandas.plotting import scatter_matrix
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

# idx = [i for i in range(1, 4)] + [6, 14]
dataset: pd.DataFrame = pd.read_csv(filepath_or_buffer="./4.csv", na_filter=True, na_values='?').iloc[:, 1:]
dataset.dropna(inplace=True)
dataset = dataset.reindex(
    ['ActualEffort', 'ObjectPoints', 'EstimatedEffort', 'RequirmentStability', 'RequirementsFlexibility',
     'PMExperience', 'OpenSource', 'LevelOfOutsourcing', 'RequiredReusability', 'PerformanceRequirements',
     'ProductComplexity', 'SecurityRequirements', 'ReliabilityRequirements', 'DevelopmentType'], axis=1)
# shape
print(dataset.shape)

# Срез данных head
print(dataset.head(20))
print('\n\n')

# Статистические сводка методом describe
print(dataset.describe())
print('\n\n')

# Матрица диаграмм рассеяния
# scatter_matrix(dataset)
# plt.show()

c: DataFrame = dataset.corr()
# mask: DataFrame = c.where(cond=lambda x: x < .25)
# mask = mask.fillna(True)
# c = corr[abs(corr) < .5]
mask = np.tril(np.ones_like(c, dtype=bool))
sns.heatmap(data=c, annot=True, linewidth=.5, mask=mask)

target_factors = ['ObjectPoints', 'EstimatedEffort', 'RequirmentStability', 'RequirementsFlexibility',
                  'SecurityRequirements', 'OpenSource', 'DevelopmentType']

X = pd.get_dummies(dataset[target_factors],
                   columns=['OpenSource', 'DevelopmentType'])  # , 'PMExperience', 'ReliabilityRequirements'
Y = dataset['ActualEffort']
# # Распределение по атрибуту class
# print(dataset.groupby('class').size())

# Separating the data into training and test data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, shuffle=False)

# Creating an instance of the Linear Regression class of the sklearn
lr = LinearRegression()

# Fitting the training data of the dataset into the model to train the model
lr.fit(X_train, Y_train)

# Printing the R-square for the trained model by passing unseen or the test data
score = lr.score(X_test, Y_test)

# Storing the predicted values of the test dataset by the model in an array
Y_pred = lr.predict(X_test)

MSE = mean_squared_error(Y_test, Y_pred)
MAE = mean_absolute_error(Y_test, Y_pred)

print(f'-------------- Линейная регрессия --------------\nMSE: {MSE}\tMAE: {MAE}')
print("R^2", score)
print('------------------------------------------------')

# Creating a dataset for the coefficient value for the intercept and independent features
result = pd.DataFrame(data=X.columns, columns=["Features"])
result["Coefficients"] = lr.coef_
result.loc[0] = ["a0", lr.intercept_]
print(result)

rf = RandomForestRegressor(n_estimators=80, max_depth=13, random_state=135771)
rf.fit(X_train, Y_train)
Y_pred = rf.predict(X_test)
score = rf.score(X_test, Y_test)

MSE = mean_squared_error(Y_test, Y_pred)
MAE = mean_absolute_error(Y_test, Y_pred)

print(f'-------------- Случайный лес --------------\nMSE: {MSE}\tMAE: {MAE}')
print("R^2: ", score)
print('----------------------------------------------')

plt.show()
