# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 11:17:28 2019

@author: ub54397

Analysis of 2019Q1 loan approval data from Lending Club
"""

#Import required packages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pandas import DataFrame

#Import the approved loan data from the Lending Club website via
#https://resources.lendingclub.com/LoanStats_2019Q1.csv.zip

#Import the raw data from the correct location. Skip the first row containing a URL...
lc_raw_data = pd.read_csv(r'<enter path here>\LoanStats_2019Q1.csv', skiprows = [0])
lc_raw_data = lc_raw_data.drop(lc_raw_data.index[[-1,-2]]) #... and the last 4 rows that don't contain data

#2. Keep key columns for analysis
lc_select_data = lc_raw_data[['grade', 'sub_grade', 'loan_amnt', 'emp_title', 'int_rate','home_ownership', 'annual_inc',\
                              'purpose', 'addr_state', 'dti', 'open_acc', 'delinq_2yrs']]

#Check the data types
print(lc_select_data.dtypes)

#Convert the interest rate from object to num by removing % and converting to float
lc_select_data['int_rate'] = (lc_select_data['int_rate'].str.split()).apply(lambda x: float(x[0].replace('%', '')))
print(lc_select_data.dtypes)

#Drop rows with at least 1 missing value in any column
lc_select_data = lc_select_data.dropna()

#Print out descriptive statistics of the data
lc_select_data.describe()

#Remove data where annual income and dti are more the mean + 3 stdev as outliers
lc_clean_data = lc_select_data.loc[(lc_select_data['annual_inc'] <= lc_select_data['annual_inc'].quantile(0.9))]
lc_clean_data = lc_clean_data.loc[(lc_clean_data['dti'] <= lc_clean_data['dti'].quantile(0.9))]

#Print out descriptive statistics of the cleaned data
lc_clean_data.describe()

"""
Descriptive plots of the data
"""
sns.distplot(lc_clean_data['loan_amnt'])
plt.title('Distribution of Loan Amounts')
#The loan amounts issued peak at multiples of 10K, with $10K being most popular

#Splitting the histograms by grade, we can see that most volume comes from grades A through D
g = sns.FacetGrid(lc_clean_data, col = 'grade', hue = 'grade')
g = g.map(plt.hist, "loan_amnt")
plt.title('Distribution of Loan Amounts by Grade')

#Let's keep just the A grade for further analyses
lc_A_clean = lc_clean_data.loc[(lc_clean_data['grade'] == 'A')]

#Plotting total dollars lent by sub-grade
sns.barplot(x='sub_grade', y='loan_amnt', data = lc_A_clean, estimator = sum, order = ['A1','A2','A3','A4','A5'])
plt.title('Total Loan Amount by Grade')
#Most of the lending happens in the A4 sub-grade

#Let us now look at some relationships between int rate and risk factors like DTI, income and delinquency
#g = sns.FacetGrid(lc_select_data, col = 'grade')
g = sns.FacetGrid(lc_A_clean, col = 'sub_grade', hue = 'sub_grade', col_order = ['A1','A2','A3','A4','A5'])
g = (g.map(plt.scatter, "loan_amnt", "int_rate", edgecolor = 'w', ).add_legend())
plt.title('Interest Rates vs Loan Amount by Grade')
#The interest rate seems to vary by sub grade within each grade regardless of loan amount

#How does the loan amount correlate with other variables?
sns.heatmap(lc_A_clean.corr(), annot = True)
plt.title('Heatmap of Correlations amonng Different Variables')
#Examining the heatmap, it seems that the loan amount is most correlated to income

#Let's examine this via a scatter plot
sns.lmplot(x='annual_inc', y = 'loan_amnt', col = 'sub_grade', hue = 'sub_grade',data = lc_A_clean, col_order = ['A1','A2','A3','A4','A5'])
#There seems to be positive relationship between the two

#Examining loan amount by home ownership
#Total by home ownership
sns.barplot(x='home_ownership', y='loan_amnt', data = lc_A_clean, estimator = sum)
plt.title('Total Loan Amount by Home Ownership')

sns.barplot(x='home_ownership', y='loan_amnt', data = lc_A_clean)
plt.title('Mean Loan Amount by Home Ownership')

#Since most of the loans are towards renters and mortgage payers, let's run a t-test to see if
#there is a difference in the mean loan amount for these 2 groups
from scipy.stats import ttest_ind

renter = lc_A_clean[lc_A_clean['home_ownership'] == 'RENT']
mtg_payer = lc_A_clean[lc_A_clean['home_ownership'] == 'MORTGAGE']

ttest_ind(renter['loan_amnt'], mtg_payer['loan_amnt'])
#The test returns a very small p-value, thereby rejecting the null hypothesis
#that there is no difference in the mean loan amounts by renter or mortgage payer