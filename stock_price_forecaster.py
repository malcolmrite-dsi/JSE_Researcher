import matplotlib.pyplot as plt
import pickle

import numpy as np

#Importing custom library for web scraping
import request_web as rwb

from pmdarima.arima import auto_arima
#Saving images as tempfiles
import tempfile
from datetime import date

import os

class StockForecaster():
    def forecaster(code, duration):
        with open(f'Stock Price Models/{code}_model.pkl', 'rb') as pkl:
            today = date.today()
            # Get day number, to know how many days to predict from
            dayNum = today.strftime("%d")

            #Get the number of days to predict from the slider on the app
            predictDays = StockForecaster.get_predict_days(duration)
            #calculate number of days since the model was updated
            buffer = int(dayNum) + 30 - 13

            mod = pickle.load(pkl)

            result = mod.predict(buffer + predictDays)

            result = np.exp(result) / 100

            todaysPrice = rwb.FinancialGetter.get_stock_price(code)

            confidence = round(((todaysPrice - result[buffer - 1])/todaysPrice), 4) * 100

            prediction = round(((result[buffer + predictDays - 1] - todaysPrice)/todaysPrice), 4) * 100 + confidence


        return prediction, confidence

    def get_predict_days(duration):
        if duration == "1 Day":
            days = 1
        elif duration == "3 Days":
            days = 3
        elif duration == "1 Week":
            days = 7
        elif duration == "1 Month":
            days = 30
        else:
            days = 365

        return days
