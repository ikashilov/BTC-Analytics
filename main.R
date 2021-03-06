# ==================================================================
#             BED-2056: Introduction to Data Science
#                   Final Project
#                   UiT Fall 2019
#                   Ivan Kashilov
# ==================================================================
rm(list=ls())
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

library(dplyr)
library(ggplot2)
library(quantmod)
library(tidyverse)
library(lubridate)

# ====================================================================
#                        Get Data
# ====================================================================

stock_data <- getSymbols('BTC-USD', src='yahoo', auto.assign=FALSE,
                                    from='2018-12-01', to='2019-12-01')
#for forecasting
#write.zoo(stock_data, 'BTC-USD.csv', sep=';')

chartSeries(stock_data)
#browseURL('https://www.quantmod.com/examples/charting')

tweets <- read.csv('./text/data/btc_year_full_sentiments.csv', stringsAsFactors=FALSE)
# Sort by date
tweets <- tweets %>% arrange(ymd_hms(tweets$date)) 


# ===================================================================
#                      Avg daily tweets number 
# ===================================================================
per_day <- tweets %>% group_by(date = as.Date(ymd_hms(date))) %>%
                      summarise(count = n())

ggplot(per_day, aes(x=count)) + 
  geom_histogram(aes(y=..density..), colour="black", fill="white")+
  geom_density(alpha=.2, fill="#FF6666") 


# ===================================================================
#                      Rolling Sentimnts
# ===================================================================
roll_sent <- tweets %>% group_by(date = as.Date(ymd_hms(date))) %>%
                   summarise(mean_sent = mean(sentiment_cl))

ggplot(roll_sent, aes(x=date, y=mean_sent)) + geom_line() + ylab('sent')
                                              ggtitle('Sentiments rolling mean')
                                              
stock_data$`BTC-USD.Adjusted` %>% autoplot()                                              
                                              
# ===================================================================
#                      Daily Returns
# ===================================================================
library(iClick)
library(PerformanceAnalytics)
stock_ret <- na.omit(periodReturn(stock_data,
                                  period='daily',
                                  type='arithmetic'))
names(stock_ret) <- c('Daily returns')
calendarHeat(stock_ret, ncolors = 99, color = "r2b", date.form = "%Y-%m-%d")


daily_sent <- as.xts(roll_sent$mean_sent, order.by=roll_sent$date)
names(daily_sent) <- c('Avg daily sentiment')
calendarHeat(daily_sent, ncolors = 99, color = "r2b", date.form = "%Y-%m-%d")

                                              
# ===================================================================
#                        Emotions
# ===================================================================
                                         
library(syuzhet)
# Analyzing the full dataset does not make any sence, plus it will take forever
# Let's do it for the last month as the example
tmp <- tweets %>% subset(date > as.Date('2019-11-01'))

sent2 <- get_nrc_sentiment(tmp$text)
sent3 <- as.data.frame(colSums(sent2))
sent3 <- rownames_to_column(sent3) 
colnames(sent3) <- c("emotion", "count")

ggplot(sent3, aes(x = emotion, y = count, fill = emotion)) +
  geom_bar(stat = "identity") + theme_minimal() +
  theme(legend.position="none", panel.grid.major = element_blank()) +
  labs(x = "Emotion", y = "Total Count") + ggtitle("Tweets Sentiments 'Emotions'")

