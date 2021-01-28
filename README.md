# BTC-Analytics
Final project for BED-2056 (Data Science) course UiT Fall 2019

*This documnet will guide through all parts of this project. All additional explantions can be found in source files.*  
You can access the report directly from your browser by going [here](https://ikashilov.github.io/BTC-Analytics/) Thanks to [GitHub Pages](https://pages.github.com/) 

## Chapter 0: Intro
- *Tesla's stock jumped 2.5% after Tencent said it amassed a 5% stake in the electric car maker.* 
- *Ocwen jumped 12% premarket after disclosing it reached a deal with New York regulators that will end third-party monitoring of its business within the next three weeks. In addition, restrictions on buying mortgage-servicing rights may get eased.*  
- *Cara Therapeutics's shares surged 16% premarket, after the biotech company reported positive results in a trial of a treatment for uremic pruritus.*  
  
So as we can see, the news have a huge affect to stock market. The goal of this project is to test it on the most volatile asset - cryptocurrency Bitcoin. 
Due to the complexity of the task, the final submission consists of severial parts:  
- obtaining text data  
- cleaning texts  
- sentiment analysis  
- combining text's sentimets with the stock market data  
- price forecasting

## Chapter 1: Scraping data
Exploring the internet I found only two financial tweets datasets, both from Kaggle and both of them were not suitable for the project so I decided to find data myself. Choosing the source of the data was pretty naive: it could be official articles from financial magazines or social media data.
The first approach involves deep NLP analysis and need an access to any 'financial articecles archive' which is not so strightforfard. So I decided to scrape data data from Twitter. And it can be also done in two ways: First - by registrating developer account, which is quite expencive. Or secondly - by scraping tweets directly from twitter using twitter advanced search:
https://twitter.com/search-advanced?lang=en
The main problem of such approach is that twitter shows the result on a web page with only 20 first tweets, to get more you need to scroll the page down. And this feature makes impossible parsing a static web page using well knows instaruments such as *Beatifull Soup* library for Python. I use the first obvious solution: to imitate user actions with *Selenium* library for Python as well.
The original source code for bot I implemented can be found **[./text/twitter_bot.py]**. It allows you to scrape data by keywords, hashtags, specifying date range and language. The main problem of this solution is that for a big date ranges such as month or more, we need to scroll the page down too many times, which leads to overlaoding crashes the program. So, to scrape tweets for a big period I generate daily date pairs and scrape data multiple times for each day in a period. The advantage of this approach is that it can be parallelized. Jupypter notebook with this part can be found here **[./text/Scrape tweets.ipynb]**

## Chapter 2: Cleaning data
I scraped tweets for the whole year 01/12/2018 - 01/12/2019 and for each tweet I have:  
- Timestamp  
- Raw text  
- Number of likes  
- Number of retweets  
The last two variables represent the sources popularity can be used to filter data
The raw tweets have a lot of emoji symbols, unicode symbols, links and special symbols.
Notebook **[./text/Tweets cleaning.ipynb]** gets rid of all uselless symbols and cleans the texts.

## Chapter 3: Sentiment analysis
To work further with the text data we need to somehow extract the meaning from texts or in other words - to perform a sentiment analysis https://en.wikipedia.org/wiki/Sentiment_analysis. This is a wide NLP (natural language processing) task and the easiest type of such analysis is a polarity analisys. So we basically want to know, whether the sentence (tweet in this case) is positive, negative or neutral.
It can be done it two general approaches:  
- Using bag-of-words model which represnts sentences as vectors with length of the vocabulary (number of words).It's naive approach but rather fast and easy to implement. But the main disadvantage is that it cannot deal with words which are not in vocabulary  **[./text/NLTK Sentiment Analysis.ipynb]** (at the bottom you can see the word cloud for raw tweets)
- Using LSTM neural networks which works similarly as human brains - by looking back at the context, trying to understand the meaning of the sentence. **[./text/LSTM Sentiment Analysis.ipynb]** But it takes lot of time to work so the solution should be run in Google Coloab: **[https://drive.google.com/open?id=1MeW8r7qOZxjih4348dpFKjHxhxe-s5pJ]** Shared access was enabled.

## Chapter 4: Combing text and stock data

After executing all the previous steps we end up with dataset:
- Timestamp  
- Raw text  
- Cleaned text  
- Number of likes  
- Number of retweets 
- Raw text sentiments
- Cleaning text sentiments
I downloaded bitcoin stock prices from Yahoo Fiance https://finance.yahoo.com/, calculated daily returns and combine everything with the obtained dataset. R script: **[./main.R]** shows the pipeline and R mardown report: **[./report.Rmd]** with its output **[./report.html]** can provide the results.


## Chapter 5: Forecasting
The file **[./forecast/BTC predict.ipynb]** shows standard approach of time series forecasting with recurrent neural networks (using rolling window technique). The results again are not sufficient, because of ultra high non constant volatility (Trainig for more epochs leads to overfitting). In prospect, I am planning to add ARIMA (or SARIMA, but I cannot see any seasonal component in BTC prices) Link to Cornell: https://arxiv.org/abs/1904.05315

## Closing thoughts
Although the results can not be used in practice, or even no correlation was found, I found this approach very promising. The problems of current solution are:
- Texts were not filtered in any way. So it could be some tweets about kittens but with #bitcon #crypto hastags. Also the popularity is important: there were a lot of tweets with 0 likes
- Models used for sentiment analysis were trained on regualar texts which were not specified in any way  

## Contents:
Twitter bot **[./text/twitter_bot.py]** and data scraping notebook **[./text/twitter_bot.py]**   
Cleaning tweets notebook **[./text/Tweets cleaning.ipynb]**  
Naive sentiment analysis **[./text/NLTK Sentiment Analysis.ipynb]**   
Neural network's sentiment analysis **[./text/LSTM Sentiment Analysis.ipynb]** external link to google colab
**[https://drive.google.com/open?id=1MeW8r7qOZxjih4348dpFKjHxhxe-s5pJ]**  
R code which puts everything together **[./main.R]** its RMardown output **[./report.html]**   

