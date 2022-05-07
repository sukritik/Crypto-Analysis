# -*- coding: utf-8 -*-
"""R Kernel - Data Mining Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UI2qwRHO5_groEgQntYPw1N0uxs-VIpo

## **Importing Modules**
"""

# # Install modules

# install.packages('lubridate')
# install.packages('zoo')
# install.packages('ggplot2')
# install.packages('reshape2')
# install.packages("glmnet")
# install.packages("randomForest")
# install.packages("reshape2")

# Import modules

options(warn = -1)
library(lubridate)
library(dplyr)
library(stringr)
library(zoo)
library(ggplot2)
library('reshape2')
library('glmnet')
library(randomForest)
library(reshape2)

"""## **Data Preprocessing**"""

# reading files from GITHUB having dependent and independent variables
df1<-read.csv('https://raw.githubusercontent.com/DN612/Crypto-Analysis/main/Data%20Sources/Data_Macro.csv',header = TRUE)
df2<-read.csv('https://raw.githubusercontent.com/DN612/Crypto-Analysis/main/Data%20Sources/Data_Macro2.csv',header = TRUE)
df1 <-df1[2:nrow(df1),]
head(df1)

df2 <-df2[2:nrow(df2),]
head(df2)

# Data type of the dataframe
typeof(df1$X.NAME.)

# converting to date time
df1$X.NAME.<-as.Date(df1$X.NAME., format =  "%d/%m/%Y")
df2$X.NAME.<-as.Date(df2$X.NAME., format =  "%d/%m/%Y")

# merging the dataframes
df <- merge(df1, df2, by="X.NAME.")
head(df)

print(paste('Columns of the entire dataframe',ncol(df)))
print(paste('Columns of the first dataframe',ncol(df1)))
print(paste('Columns of the second dataframe',ncol(df2)))

# Setting index as Date
names(df)[1] <- 'Date'
print(nrow(df))
print(ncol(df))
head(df)

# ADS index
ads_index<-read.csv('https://raw.githubusercontent.com/DN612/Crypto-Analysis/main/Data%20Sources/ADS_Index.csv',header = TRUE)
head(ads_index)

# Changing to date time
ads_index$X <- str_replace_all(ads_index$X, ":", "/")
ads_index$X<-as.Date(ads_index$X)
head(ads_index)

# Renaming date column
names(ads_index)[1] <- 'Date'
tail(ads_index)

head(df)

df <- merge(df, ads_index, by='Date',x.all=TRUE)
print(nrow(df))
print(ncol(df))
head(df)

# Dropping data for which no crypto prices exists and convert all columns to double and indexing at Date
rownames(df) = df$Date
print(nrow(df))
df=df[-c(1)]
df = subset(df, select = -c(GBTC.US.Equity) )
df = mutate_all(df, function(x) as.double(x))
print(nrow(df))
print(ncol(df))

head(df)

returns_df = (lead(df)-df)/df
head(returns_df)

head(df)
write.csv(df, 'Data.csv')

"""## **Data Analysis**"""

df = read.csv("https://raw.githubusercontent.com/DN612/Crypto-Analysis/main/Data%20Sources/BTC_features.csv")
df$Date = as.Date(df$Date, format="%Y-%m-%d")
# df
rownames(df) <- df$Date
drops <- c('Date')
df = df[ , !(names(df) %in% drops)]
head(df)

options(repr.plot.width=14, repr.plot.height=7)
df_colnames = colnames(df)
options(repr.width=40)
par(mfrow=c(3,5))
for (col in df_colnames) {
  if (col != 'Bitcoin.Core..BTC..Price'){
    plot((df[col][,1]-min(df[col][,1]))/max(df[col][,1]), type='l', main=col,xlab='Date',ylab='Normalised Levels',col='blue',ylim=c(0,2))
    lines((df['Bitcoin.Core..BTC..Price'][,1]-min(df['Bitcoin.Core..BTC..Price'][,1]))/max(df['Bitcoin.Core..BTC..Price'][,1]) , col = "red")
    legend('topleft', legend=c(col, "Bitcoin.Core..BTC..Price"),
       col=c("blue", "red"), lty=1:1, cex=0.7)
  }
    

}

#returns of series
diff = (lead(df)-df)/df
diff = diff[complete.cases(diff),]
diff$label = lead(diff$Bitcoin.Core..BTC..Price)*100
diff = diff[complete.cases(diff$label),]
head(diff)

# weekly realized volatility

diff$std_BTC_returns = rollapplyr(diff['Bitcoin.Core..BTC..Price'], 5, sd, fill = 0)*100

head(diff)

options(repr.plot.width=14, repr.plot.height=7)
options(repr.width=40)
par(mfrow=c(3,5))
df_colnames = colnames(diff)
for (col in df_colnames) {
  if (col != 'Bitcoin.Core..BTC..Price'){
    plot(diff[col][,1], type='l', main=col,xlab='Date',ylab='Differenced Levels for stationarity',col='darkgrey')
  }
}

train_size = floor(0.75 * nrow(diff))
train_data = diff[1:train_size, ]
test_data = diff[train_size:nrow(diff), ]

train_y = train_data$label
drops <- c('label')
train_X = train_data[ , !(names(train_data) %in% drops)]

head(train_X)

std_train_X = scale(train_X)
std_train_data = cbind(std_train_X, train_y)
colnames(std_train_data)[ncol(std_train_data)] = 'label'
head(std_train_data)

# creating correlation matrix
corr_mat <- round(cor(std_train_data, method='pearson'),2)
 
# reduce the size of correlation matrix
melted_corr_mat <- melt(corr_mat)
# head(melted_corr_mat)

options(repr.plot.width=20, repr.plot.height=20)
 
# plotting the correlation heatmap
ggplot(data = melted_corr_mat, aes(x=Var1, y=Var2,
                                   fill=value)) +
geom_tile() +
geom_text(aes(Var2, Var1, label = value),
          color = "black", size = 4) + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))

corr_mat

write.csv(as.data.frame(corr_mat),'Correlation matrix.csv')

# cor_matrix_rm[upper.tri(corr_mat)] <- 0
# diag(corr_mat) <- 0
count_list = c()
for(row in 1:nrow(corr_mat)) {
    count=0
    for(col in 1:ncol(corr_mat)) {
      if(abs(corr_mat[row,col]) >= 0.75) {

        count = count+1
      }
    }
    count_list = c(count_list, count)
}

corr_add = as.data.frame(cbind(rownames(corr_mat), count_list))
corr_add[order(corr_add$count_list),c(1,2)]

drops <- c('Annual.Hash.Growth','Block.Height','Block.Interval','Block.Size','Daily.Transactions','Difficulty','Fee.Percentage','Fee.Rate','Two.Week.Hash.Growth','Hash.Rate','Inflation.Rate','Price.Volatility','Bitcoin.Core..BTC..Price','Quarterly.Hash.Growth','Total.Transactions','Transaction.Size','Avg..UTXO.Amount','Velocity...Daily','Velocity...Quarterly','Velocity.of.Money','std_BTC_returns','label')
df_new = diff[ , (names(diff) %in% drops)]
head(df_new)

train_size = floor(0.75 * nrow(df_new))
train_data = df_new[1:train_size, ]
test_data = df_new[train_size:nrow(df_new), ]

train_y = train_data$label

# creating correlation matrix
corr_mat <- round(cor(train_data, method='pearson'),2)
 
# reduce the size of correlation matrix
melted_corr_mat <- melt(corr_mat)
# head(melted_corr_mat)

options(repr.plot.width=10, repr.plot.height=10)
 
# plotting the correlation heatmap
ggplot(data = melted_corr_mat, aes(x=Var1, y=Var2,
                                   fill=value)) +
geom_tile() +
geom_text(aes(Var2, Var1, label = value),
          color = "black", size = 4) + theme(axis.text.x = element_text(angle = 90, vjust = 1.5, hjust=1))

count_list = c()
for(row in 1:nrow(corr_mat)) {
    count=0
    for(col in 1:ncol(corr_mat)) {
      if(abs(corr_mat[row,col]) >= 0.75) {

        count = count+1
      }
    }
    count_list = c(count_list, count)
}

corr_add = as.data.frame(cbind(rownames(corr_mat), count_list))
corr_add[order(corr_add$count_list),c(1,2)]

"""#### EDA on Macro variables"""

# Macro variables 
df_macro = read.csv("https://raw.githubusercontent.com/DN612/Crypto-Analysis/main/Data%20Sources/Weekday_macro.csv")
df_macro$Date = as.Date(df_macro$Date, format="%d/%m/%Y")
# # df
rownames(df_macro) <- df_macro$Date
drops <- c('Date')
df_macro = df_macro[ , !(names(df_macro) %in% drops)]
head(df_macro)

options(repr.plot.width=14, repr.plot.height=7)
df_colnames = colnames(df_macro)
options(repr.width=40)
par(mfrow=c(3,5))

for (col in df_colnames) {
  if (col != 'Bitcoin.Core..BTC..Price'){
    plot((df_macro[col][,1]-min(df_macro[col][,1]))/max(df_macro[col][,1]), type='l', main=col,xlab='Date',ylab='Normalised Levels',col='blue',ylim=c(0,2))
    lines((df_macro['Bitcoin.Core..BTC..Price'][,1]-min(df_macro['Bitcoin.Core..BTC..Price'][,1]))/max(df_macro['Bitcoin.Core..BTC..Price'][,1]) , col = "red")
    legend('topleft', legend=c(col, "Bitcoin.Core..BTC..Price"),
       col=c("blue", "red"), lty=1:1, cex=0.7)
  }
}

#returns of series
diff_macro = (lead(df_macro)-df_macro)/df_macro
diff_macro = diff_macro[complete.cases(diff_macro),]
diff_macro$label = lead(diff_macro$Bitcoin.Core..BTC..Price)*100
diff_macro = diff_macro[complete.cases(diff_macro$label),]
head(diff_macro)

df_colnames = colnames(diff_macro)
options(repr.plot.width=14, repr.plot.height=7)
par(mfrow=c(3,5))

for (col in df_colnames) {
  if (col != 'Bitcoin.Core..BTC..Price'){
    plot(diff_macro[col][,1], type='l', main=col,xlab='Date',ylab='Differenced Levels for stationarity',col='darkgrey')   
  }
}

train_size = floor(0.75 * nrow(diff_macro))
train_data = diff_macro[1:train_size, ]
drops <- c('Sentiment.Score')
train_data = train_data[ , !(names(train_data) %in% drops)]
test_data = diff_macro[train_size:nrow(diff_macro), ]

train_y = train_data$label
drops <- c('label')
train_X = train_data[ , !(names(train_data) %in% drops)]

head(train_X)

# creating correlation matrix
corr_mat <- round(cor(train_data, method='pearson'),2)
 
# reduce the size of correlation matrix
melted_corr_mat <- melt(corr_mat)
# head(melted_corr_mat)

options(repr.plot.width=10, repr.plot.height=10)
 
# plotting the correlation heatmap
library(ggplot2)
ggplot(data = melted_corr_mat, aes(x=Var1, y=Var2,
                                   fill=value)) +
geom_tile() +
geom_text(aes(Var2, Var1, label = value),
          color = "black", size = 4) + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))

count_list = c()
for(row in 1:nrow(corr_mat)) {
    count=0
    for(col in 1:ncol(corr_mat)) {
      if(abs(corr_mat[row,col]) >= 0.75) {

        count = count+1
      }
    }
    count_list = c(count_list, count)
}

corr_mat

write.csv(as.data.frame(corr_mat),'Correlation matrix macro.csv')

corr_add = as.data.frame(cbind(rownames(corr_mat), count_list))
corr_add[order(corr_add$count_list),c(1,2)]

drops <-c('SPX.Index','VVIX.Index','VIX.Index','Sentiment.Score')
dfmacro_new = diff_macro[ , !(names(diff_macro) %in% drops)]
head(dfmacro_new)

train_size = floor(0.75 * nrow(dfmacro_new))
train_data = dfmacro_new[1:train_size, ]
test_data = dfmacro_new[train_size:nrow(dfmacro_new), ]

train_y = train_data$label

# creating correlation matrix
corr_mat <- round(cor(train_data, method='pearson'),2)
 
# reduce the size of correlation matrix
melted_corr_mat <- melt(corr_mat)
# head(melted_corr_mat)

options(repr.plot.width=10, repr.plot.height=10)
 
# plotting the correlation heatmap
ggplot(data = melted_corr_mat, aes(x=Var1, y=Var2,
                                   fill=value)) +
geom_tile() +
geom_text(aes(Var2, Var1, label = value),
          color = "black", size = 4) + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))

df = read.csv("https://raw.githubusercontent.com/DN612/Crypto-Analysis/main/Final.csv")
df$Date = as.Date(df$Date, format="%d-%m-%Y")
#df
# print(nrow(df))
# print(ncol(df))
rownames(df) <- df$Date
drops <- c('Date')
df = df[ , !(names(df) %in% drops)]
head(df)

df_minussent = df[-(ncol(df)-2)]
diff = (lead(df_minussent)-df_minussent)/df_minussent
# print(dim(diff))
#print(colnames(diff))
diff = diff[complete.cases(diff),]
diff$Sentiment.Score = df$Sentiment.Score[-1]
# print(length(df$Sentiment.Score))
print(dim(diff))
diff$label = lead(diff$Bitcoin.Core..BTC..Price)*100
diff = diff[complete.cases(diff$label),]

diff$std_BTC_returns = rollapplyr(diff['Bitcoin.Core..BTC..Price'], 5, sd, fill = 0)*100

head(diff)

drops <- c('SPX.Index','VVIX.Index','VIX.Index')
dffull_new = diff[ , !(names(diff) %in% drops)]
head(dffull_new)

drops <- c('Lumber.prices','WTI.Oil','DIA.US.Index','CNYUSD.Curncy','EURUSD.Curncy','GDX.US.Equity','SHCOMP.Index','TWSE.Index','ADS_Index','Google.trends','Annual.Hash.Growth','Block.Height','Block.Interval','Block.Size','Daily.Transactions','Difficulty','Fee.Percentage','Fee.Rate','Two.Week.Hash.Growth','Hash.Rate','Inflation.Rate','Price.Volatility','Bitcoin.Core..BTC..Price','Quarterly.Hash.Growth','Total.Transactions','Transaction.Size','Avg..UTXO.Amount','Velocity...Daily','Velocity...Quarterly','Velocity.of.Money','Sentiment.Score','std_BTC_returns','label')
dffull_new = diff[ , (names(diff) %in% drops)]
head(dffull_new)

write.csv(dffull_new,'FullDataset.csv')

options(repr.plot.width=14, repr.plot.height=7)
options(repr.width=40)
par(mfrow=c(1,2))
plot((df['Google.trends'][,1]-min(df['Google.trends'][,1]))/max(df['Google.trends'][,1]), type='l', main='Google trends vs Bitcoin Prices',xlab='Date',ylab='Normalised Levels',col='blue',ylim=c(0,2))
lines((df['Bitcoin.Core..BTC..Price'][,1]-min(df['Bitcoin.Core..BTC..Price'][,1]))/max(df['Bitcoin.Core..BTC..Price'][,1]) , col = "red")
legend('topleft', legend=c('Google.trends', "Bitcoin.Core..BTC..Price"),
col=c("blue", "red"), lty=1:1, cex=0.7)

options(repr.width=40)
# par(mfrow=c(3,5))
plot((df['Sentiment.Score'][,1]-min(df['Sentiment.Score'][,1]))/max(df['Sentiment.Score'][,1]), type='l', main='Sentiment.Score vs Bitcoin Prices',xlab='Date',ylab='Levels',col='blue',ylim=c(0,2))
lines((df['Bitcoin.Core..BTC..Price'][,1]-min(df['Bitcoin.Core..BTC..Price'][,1]))/max(df['Bitcoin.Core..BTC..Price'][,1]) , col = "red")
legend('topleft', legend=c('Sentiment.Score', "Bitcoin.Core..BTC..Price"),
col=c("blue", "red"), lty=1:1, cex=0.7)

#acf plot
options(repr.plot.width=14, repr.plot.height=7)
options(repr.width=40)
par(mfrow=c(1,2))
acf(diff['label'],main='ACF of the Bitcoin prices', xlab='Lags')

"""## Baseline Model"""

pacf(diff['label'],main='Partial Autocorrelation of the Bitcoin prices', xlab='Lags')

library(forecast)
fitCrypto = auto.arima(diff['label'])
fitCrypto

#install.packages('rugarch')
library(rugarch)
garch.model.t = ugarchspec(mean.model = list(armaOrder=c(0,1)),
variance.model=list(garchOrder=c(1,1)),
distribution.model="std")
#Train and test split
r=floor(0.75*nrow(diff))
garchFit = ugarchfit(data=diff[1:r,'label'],spec=garch.model.t)
predGARCH = ugarchforecast(garchFit, n.ahead = 474)
### Predictions start at end of series
plot(diff[(nrow(diff)-473):nrow(diff),'label'],type="l",xlab='Date',ylab='Levels')
lines(fitted(predGARCH),col="red",lwd=4)

# install.packages('Metrics')
library(Metrics)

rmse(diff[(nrow(diff)-473):nrow(diff),'label'], fitted(predGARCH))