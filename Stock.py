import requests
import json
import Market
import stock_api_exceptions
import matplotlib.pyplot as plt
import random

api_key = "pk_e4cd3161272b47369625df7d517b8714"

market = Market.Market()


class Stock:
    def __init__(self, ticker, amount_of_stocks=0, cost=-1, purchase_date="False"):
        self._amount_of_stocks = int(amount_of_stocks)
        self._ticker = str(ticker)
        self._cost = int(cost)
        if purchase_date == 'False':
            self._purchase_date = '-'
        else:
            self._purchase_date = str(purchase_date)
        # TODO Handle Exception
        try:
            api_request = requests.get(
                "https://cloud.iexapis.com/stable/stock/" + self._ticker + "/batch/?types=quote,stats,logo,company&token=" + api_key)
            api = json.loads(api_request.content)
            self._company_name = api['quote']['companyName']
            self._price = api['quote']['latestPrice']
            self._open_price = api['quote']['open']
            # if data is None set -
            if not self._open_price:
                self._open_price = '-'
            self._close_price = self.get_updated_close_price(api)
            self._market_cap = get_market_cap(api['quote']['marketCap'])
            self._bid_price = api['quote']['iexBidPrice']
            self._bid_size = api['quote']['iexBidSize']
            self._ask_price = api['quote']['iexAskPrice']
            self._ask_size = api['quote']['iexAskSize']
            self._week_52_range = str(api['quote']['week52Low']) + " - " + str(api['quote']['week52High'])
            self._avg_total_volume = api['quote']['avgTotalVolume']
            self._volume = api['quote']['latestVolume']
            if not self._avg_total_volume:
                self._avg_total_volume = '-'
            if not self._volume:
                self._volume = '-'
            self._daily_change = api['quote']['changePercent']
            self._daily_change_money = api['quote']['change']
            self._daily_low = api['quote']['low']
            self._daily_high = api['quote']['high']
            self._daily_range = '-'
            self._ytd_change = api['quote']['ytdChange']
            # get stock stats that do not appear on both api calls
            # api_request = requests.get(
            #     "https://cloud.iexapis.com/stable/stock/" + self._ticker + "/stats?token=" + api_key)
            # self.check_response_code(api_request)
            # api = json.loads(api_request.content)
            self._beta = api['stats']['beta']
            self._pe_ratio = api['stats']['peRatio']
            self._eps = api['stats']['ttmEPS']
            self._next_earnings_date = api['stats']['nextEarningsDate']
            self._dividend_yield = api['stats']['dividendYield']
            self._ex_dividend_date = api['stats']['exDividendDate']
            self.check_if_not_none()
            if cost == -1 or self._amount_of_stocks == -1:  # if stock not purchased
                self._amount_of_stocks = self._amount_of_stocks
                self._cost = '-'
                self._stock_holdings = '-'
                self._total_change_money = '-'
            else:
                self._stock_holdings = self._amount_of_stocks * self._price  # current stock holding
                self._total_change_money = (self._price * self._amount_of_stocks) - (
                        self._cost * self._amount_of_stocks)
            #     Get Logo
            # api_request = requests.get(
            #     "https://cloud.iexapis.com/stable/stock/" + self._ticker + "/logo?token=" + api_key)
            # self.check_response_code(api_request)
            # self._logo = json.loads(api_request.content)['url']
            self._logo = api['logo']['url']
            # api_request = requests.get(
            #     "https://cloud.iexapis.com/stable/stock/" + self._ticker + "/company?token=" + api_key)
            # self.check_response_code(api_request)
            # api = json.loads(api_request.content)
            self._company_description = api['company']['description']
            self._sector = api['company']['sector']

        except stock_api_exceptions.UnknownSymbolException as e:
            print(str(e))
        except stock_api_exceptions.ServerErrorException as e:
            print(str(e))
        except Exception as e:
            print(str(e))

    def check_response_code(self, response):
        response_code = int(str(response)[11:14])
        if response_code != 200:
            if response_code == 404:
                raise stock_api_exceptions.UnknownSymbolException
            elif response_code == 500:
                raise stock_api_exceptions.ServerErrorException

    def check_if_not_none(self):
        if not self._ask_price:
            self._ask_price = '-'
            self._ask_size = ''
        if not self._bid_price:
            self._bid_price = '-'
            self._bid_size = ''
        if not self._beta:
            self._beta = '-'
        else:
            self._beta = round(self._beta, 3)
        if not self._pe_ratio:
            self._pe_ratio = '-'
        else:
            self._pe_ratio = round(self._pe_ratio, 3)
        if not self._eps:
            self._eps = '-'
        else:
            self._eps = round(self._eps, 3)
        if not self._next_earnings_date:
            self._next_earnings_date = '-'

        if not self._dividend_yield:
            self._dividend_yield = '-'
        else:
            self._dividend_yield = round(self._dividend_yield, 3)

        if not self._ex_dividend_date:
            self._ex_dividend_date = '-'

        if self._daily_low and self._daily_high:
            self._daily_range = str(str(self._daily_low) + ' - ' + str(self._daily_high))

    def get_ticker(self):
        return self._ticker

    def get_price(self):
        return self._price

    def get_daily_change(self):
        return self._daily_change

    def get_amount_of_stocks(self):
        return self._amount_of_stocks

    def get_cost(self):
        return self._cost

    def get_close_price(self):
        return self._close_price

    def get_holdings(self):
        return self._stock_holdings

    def get_orignal_holdings(self):
        if self._cost == '-' or self._amount_of_stocks == '-':
            return '-'
        return self._cost * self._amount_of_stocks

    def get_stock_gain(self):
        orignal_holdings = self.get_orignal_holdings()
        if self._stock_holdings == '-' or orignal_holdings == '-':
            return '-'
        return self.calculate_percentage_change(current=self._stock_holdings, previous=orignal_holdings)

    def get_company_name(self):
        return self._company_name

    def __str__(self):
        return "Stock[ticker=" + self._ticker + ", amount_of_stocks= " + str(self._amount_of_stocks) + ", cost= " + str(
            self._cost) + ", close_price= " + str(self._close_price) + ", price=" + str(
            self._price) + ", daily_change= " + str(round(float(self._daily_change), 4)) + "%,stock_holdings= " + str(
            self._stock_holdings) + ",orignal_holdings= " + str(self.get_orignal_holdings()) + ", stock_gain= " + str(
            self.get_stock_gain()) + "%, company_name= " + self._company_name + " purchase_date=" + str(
            self._purchase_date) + ", market_cap=" + str(self._market_cap) + ", bid= " + str(
            str(self._bid_price) + ' X ' + str(self._bid_size)) + ", ask=" + str(
            str(self._ask_price) + ' X ' + str(
                self._ask_size)) + ", week_52_range= " + self._week_52_range + ", avg_total_volume = " + str(
            self._avg_total_volume) + ", volume= " + str(self._volume) + ", Beta=" + str(
            self._beta) + ", peRatio= " + str(self._pe_ratio) + ", eps=" + str(
            self._eps) + ", next_earnings_date=" + str(self._next_earnings_date) + " , dividend_yield=" + str(
            self._dividend_yield) + ", daily_range=" + str(self._daily_range) + ", ytd_change=" + str(
            self._ytd_change) + "%, exDividendDate=" + str(
            self._ex_dividend_date) + ", description=" + self._company_description + ", sector= " + str(
            self._sector) + "]"

    def calculate_percentage_change(self, current, previous):
        """
        calculate_percentage_change is a function that calculates the difference in percentge between two numbers
        :param current:
        :param previous:
        :return:
        """
        if current == previous:
            return 0
        try:
            return ((current - previous) / previous) * 100
        except ZeroDivisionError:
            return float('inf')

    def get_updated_close_price(self, api):
        """
        get_updated_close_price is a function that gets an api and returns the updated_close_price for the Stock
        :param api: api data after call
        :return: Stock correct close price
        """
        close_price = -1
        if market.is_open():
            close_price = api['quote']['previousClose']
        else:
            close_price = api['quote']['latestPrice']
        return close_price


    def convert_main_stock_data_to_json(self):
        json_dict = {'ticker': self._ticker,
                     'company_name': self._company_name,
                     'price': self._price,
                     'description': self._company_description,
                     'cost': self._cost,
                     'amount_of_stocks': self._amount_of_stocks,
                     'close_price': self._close_price,
                     'open_price': self._open_price,
                     'bid': str(str(self._bid_price) + ' X ' + str(self._bid_size)),
                     'ask': str(str(self._ask_price) + ' X ' + str(self._ask_size)),
                     'day_range': self._daily_range,
                     'week_52_range': self._week_52_range,
                     'volume': self._volume,
                     'avg_volume': self._avg_total_volume,
                     'market_cap': self._market_cap,
                     'beta': self._beta,
                     'pe_ratio': self._pe_ratio,
                     'eps': self._eps,
                     'next_earnings_date': self._next_earnings_date,
                     'dividend_yield': self._dividend_yield,
                     'ex_dividend_date': self._ex_dividend_date,
                     'ytd_change': self._ytd_change,
                     'stock_holdings': self._stock_holdings,
                     'daily_change': self._daily_change,
                     'total_change': self.get_stock_gain(),
                     'daily_change_money': self._daily_change_money,
                     'total_change_money': self._total_change_money,
                     'logo': self._logo,
                     'sector': self._sector
                     }

        if self._purchase_date != False:
            self._purchase_date = self._purchase_date
        json_dict['purchase_date'] = str(self._purchase_date)
        return json_dict

    def get_historcal_data(self, time_range):

        api_request = requests.get(
            "https://sandbox.iexapis.com/stable/stock/" + self._ticker + "/chart/" + time_range + "?chartInterval=" + str(
                get_chart_interval(time_range)) + "&token=" + 'Tsk_8d5db594bcc747f78b1d42e2d8593069')
        api = json.loads(api_request.content)
        stock_data_dict = {}
        if time_range == '1d':
            indicator = 'average'
        else:
            indicator = 'close'
        for d in api:
            stock_data_dict[d['label']] = d[indicator]
        return stock_data_dict


def average(lst):
    try:
        return sum(lst) / len(lst)
    except:
        return None


def get_market_cap(x):
    abbreviations = ["", "K", "M", "B", "T", "Qd", "Qn", "Sx", "Sp", "O", "N",
                     "De", "Ud", "DD"]
    thing = "1"
    a = 0
    while len(thing) < len(str(x)) - 3:
        thing += "000"
        a += 1
    b = int(thing)
    thing = round(x / b, 3)
    return str(thing) + " " + abbreviations[a]


def get_sector_diversity(list_of_stocks):
    sector_dict = {}
    for stock in list_of_stocks:
        sector_name = stock._sector.replace(' ', '_')
        if not sector_name in sector_dict:
            sector_dict[sector_name] = 1
        else:
            sector_dict[sector_name] = sector_dict[sector_name] + 1

    return sector_dict


def get_chart_interval(time_range):
    intervel = '5'
    if time_range == '5d':
        intervel = '60'
    elif time_range == '1m':
        intervel = '2d'
    elif time_range == '3m':
        intervel = '5d'
    elif time_range == '6m':
        intervel = '2w'
    elif time_range == 'ytd':
        intervel = '1w'
    elif time_range == '1y':
        intervel = '1m'
    elif time_range == '5y':
        intervel = '3m'
    elif time_range == 'max':
        intervel = '6m'
    else:
        intervel = '5'
    return intervel


def get_list_of_historcal_data(list_of_stocks, time_range):
    list_of_stock_dicts = []
    return_dict = {}
    for stock in list_of_stocks:
        list_of_stock_dicts.append(stock.get_historcal_data(time_range))

    for stock in list_of_stocks:
        for d in list_of_stock_dicts:
            for key in d:
                if stock.get_amount_of_stocks() != 0:
                    if str(key) in return_dict:
                        return_dict[str(key)] = return_dict[str(key)] + (
                                d[str(key)] * float(stock.get_amount_of_stocks()))
                    else:
                        return_dict[str(key)] = (d[str(key)] * float(stock.get_amount_of_stocks()))

    return return_dict


def main():
    a = Stock(ticker='INTC', amount_of_stocks=1)
    print(a)
    # cvs = Stock(ticker='CVS', amount_of_stocks=2)
    # print(get_list_of_historcal_data([a, cvs], time_range='5d'))
    # api_request = requests.get(
    #     "https://cloud.iexapis.com/stable/stock/" + 'AMZN'+ "/batch/?types=quote,stats,logo,company&token=" + api_key)
    # api = json.loads(api_request.content)
    # print(api)
    # print(api['stats']['week52change'])


if __name__ == '__main__':
    main()
