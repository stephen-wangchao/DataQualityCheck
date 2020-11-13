#point anomaly detection 10/6/2020

import pandas as pd
import pylab as plb
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import asarray as ar
import models

file_loc = "/Users/xiaoyutong/Downloads/1602517833297_ACCOUNT.xlsx"
input_df = pd.read_excel(file_loc, index_col=None, na_values=['NA'], usecols = "B,D,E,F")

dates=list(input_df['ACCOUNT.NUMBERS.DAILY.ASSETS.AS-OF-DATE'])
values=list(input_df['ACCOUNT.NUMBERS.DAILY.ASSETS.NET ASSETS'])
dates_ref=list(input_df['DATE'])
outcome_ref=list(input_df['OUTCOME'])

dates_excl=[]
for i in range(len(outcome_ref)):
    if outcome_ref[i] == "SUSPICIOUS":
        dates_excl.append(dates_ref[i])


dates_valid = []
values_valid = []

# filter out valid dates and values (remove 0 values)
# remove already detected bad data!!! (new as of 11/11/2020)
for i in range(len(values)):
    if values[i] != 0 and dates[i] not in dates_excl:
        dates_valid.append(dates[i])
        values_valid.append(values[i])

# adding rolling day average to use for calculating percentage change!!! (new as of 11/11/2020)
# calculate percentage change from index=1 till end of the list (round to 3 decimals)
dates_analysis = []
change_analysis = []
for i in range(1,len(dates_valid)):
    dates_analysis.append(dates_valid[i])
    change = round((values_valid[i] - values_valid[i-1])/values_valid[i-1],3)
    change_analysis.append(change)

# sort the percentage change and calculate the frequency of each percentage change
change_sorted = sorted(change_analysis)
total_len = len(set(change_sorted))
change_sorted_unique = [0 for i in range(total_len)]
change_sorted_freq = [0 for i in range(total_len)]
temp = 100000
i = -1
for value in change_sorted:
    if value != temp:
        i += 1
        change_sorted_unique[i] = value
        temp = value
    change_sorted_freq[i] += 1

change_sorted_prob = [x/sum(change_sorted_freq) for x in change_sorted_freq]

x = ar(change_sorted_unique)
y = ar(change_sorted_prob)

n = len(x)                         
mean = sum(x*y)/n                   
sigma = sum(y*(x-mean)**2)/n        

popt,pcov = curve_fit(models.gaus,x,y,p0=[1,mean,sigma])

#goodness of fit
change_sorted_prob_expected = [models.gaus(xdata,*popt) for xdata in change_sorted_unique]
chi_square = 0
for i in range(len(change_sorted_unique)):
    chi_square += (change_sorted_prob[i] - change_sorted_prob_expected[i])**2/change_sorted_prob[i]

print(chi_square)

#filter suspicious dates
suspicious_dates = []
for i in range(len(dates_analysis)):
    if change_analysis[i] >= mean + 2*sigma or change_analysis[i] <= mean - 2*sigma:
        suspicious_dates.append(dates_analysis[i])
print(suspicious_dates)

print("version updated!")

plt.plot(x,y,'b+:',label='data')
plt.plot(x,models.gaus(x,*popt),'ro:',label='fit')
plt.xlim(-0.1,0.1)
plt.legend()
plt.title('Fig. 1 - Fit for AUM change percentage')
mean_display = round(mean,4)
std_display = round(sigma,4)
plt.text(-0.095, 0.23, "The mean is {}".format(mean_display))
plt.text(-0.095, 0.2, "The std is {}".format(std_display))
plt.text(-0.095, 0.17, "The chi-square fit goodness is {}".format(chi_square))
plt.xlabel('AUM change percentage')
plt.ylabel('Probability')
plt.show()

