import datetime
import json
import sys
import os

import requests
from dateutil.relativedelta import relativedelta
import pandas as pd

from time import sleep


class Trends():
    """
    Pulls daily, weekly, and monthly data from Google Trends, and adjusts
    them so that it is weekly data which is relative to each other.
    It does this based on the weekly and monthly data.
    """

    def __init__(self):
        # if len(sys.argv) != 2:
        #     sys.exit("Usage: python3 trends.py keyword")

        self.start_date = datetime.date(2004, 1, 1)
        self.end_date = datetime.date.today()
        # self.keyword = sys.argv[1]

        self.kw_list = ["debt", "color", "stocks", "restaurant", "portfolio", "inflation", "housing", "dow jones", "revenue",
                        "economics", "credit", "markets", "return", "unemployment", "money", "religion", "cancer", "growth",
                        "investment", "hedge", "marriage", "bonds", "derivatives", "headlines", "profit", "society", "leverage",
                        "loss", "cash", "office", "fine", "stock market", "banking", "crisis", "happy", "car", "nasdaq",
                        "gains", "finance", "sell", "invest", "fed", "house", "metals", "travel", "returns", "gain",
                        "default", "present", "holiday", "water", "rich", "risk", "gold", "success", "oil", "war", "economy",
                        "chance", "short sell", "lifestyle", "greed", "food", "financial markets", "movie", "nyse", "ore",
                        "opportunity", "health", "short selling", "earnings", "arts", "culture", "bubble", "buy", "trader",
                        "rare earths", "tourism", "politics", "energy", "consume", "consumption", "freedom", "dividend", "world",
                        "conflict", "kitchen", "forex", "home", "cash", "transaction", "garden", "fond", "train", "labor",
                        "fun", "environment", "ring"]

        for self.keyword in self.kw_list:
            if os.path.exists(f"data/weekly/{self.keyword}.csv") and os.path.exists(f"data/daily/{self.keyword}.csv"):
                continue

            while True:
                try:
                    print(self.keyword)

                    self.pull_daily()
                    self.pull_weekly()
                    self.pull_monthly()

                    self.adjust_weekly()
                    self.adjust_daily()

                    sleep(90)

                    break
                except:
                    print("Sleeping...")
                    sleep(180)

    def pull_daily(self):
        """Pulls the daily data of the keyword specified from Google Trends."""

        print("Downloading daily data...")

        start_increment = self.start_date
        end_increment = self.start_date + relativedelta(months=+6)
        dataframe = False

        while True:
            token = self.get_token(
                f"{start_increment} {end_increment}")

            url = f"https://trends.google.com/trends/api/widgetdata/multiline/csv?req=%7B%22time%22%3A%22{str(start_increment)}%20{str(end_increment)}%22%2C%22resolution%22%3A%22DAY%22%2C%22locale%22%3A%22en-US%22%2C%22comparisonItem%22%3A%5B%7B%22geo%22%3A%7B%22country%22%3A%22US%22%7D%2C%22complexKeywordsRestriction%22%3A%7B%22keyword%22%3A%5B%7B%22type%22%3A%22BROAD%22%2C%22value%22%3A%22{self.keyword}%22%7D%5D%7D%7D%5D%2C%22requestOptions%22%3A%7B%22property%22%3A%22%22%2C%22backend%22%3A%22IZG%22%2C%22category%22%3A0%7D%7D&token={token}&tz=-120"

            if not dataframe:
                self.daily = pd.read_csv(url, header=1)
                dataframe = True
            else:
                temp = pd.read_csv(url, header=1)
                self.daily = self.daily.append(temp, ignore_index=True)

            # Daily data can be downloaded in 6-month increments.
            start_increment += relativedelta(months=+6)
            end_increment += relativedelta(months=+6)

            if start_increment > self.end_date:
                self.daily = self.daily.rename(
                    columns={"Day": "Date", f"{self.keyword}: (United States)": "relative_frequency"})
                return
            else:
                # Remove overlap.
                self.daily = self.daily[:-1]

    def pull_weekly(self):
        """Pulls the weekly data of the keyword specified from Google Trends."""

        print("Downloading weekly data...")

        start_increment = self.start_date
        end_increment = self.start_date + relativedelta(years=+5)
        dataframe = False

        while True:
            token = self.get_token(f"{start_increment} {end_increment}")

            url = f"https://trends.google.com/trends/api/widgetdata/multiline/csv?req=%7B%22time%22%3A%22{str(start_increment)}%20{str(end_increment)}%22%2C%22resolution%22%3A%22WEEK%22%2C%22locale%22%3A%22en-US%22%2C%22comparisonItem%22%3A%5B%7B%22geo%22%3A%7B%22country%22%3A%22US%22%7D%2C%22complexKeywordsRestriction%22%3A%7B%22keyword%22%3A%5B%7B%22type%22%3A%22BROAD%22%2C%22value%22%3A%22{self.keyword}%22%7D%5D%7D%7D%5D%2C%22requestOptions%22%3A%7B%22property%22%3A%22%22%2C%22backend%22%3A%22IZG%22%2C%22category%22%3A0%7D%7D&token={token}&tz=-120"

            if not dataframe:
                self.weekly = pd.read_csv(url, header=1)
                dataframe = True
            else:
                temp = pd.read_csv(url, header=1)
                self.weekly = self.weekly.append(temp, ignore_index=True)

            # Weekly data can be downloaded in 5-year increments.
            start_increment += relativedelta(years=+5)
            end_increment += relativedelta(years=+5)

            if start_increment > datetime.date.today():
                self.weekly = self.weekly.rename(
                    columns={"Week": "Date", f"{self.keyword}: (United States)": "relative_frequency"})
                return

    def pull_monthly(self):
        """Pulls the monthly data of the keyword specified from Google Trends."""

        print("Downloading monthly data...")

        token = self.get_token(f"{self.start_date} {self.end_date}")

        url = f"https://trends.google.com/trends/api/widgetdata/multiline/csv?req=%7B%22time%22%3A%22{str(self.start_date)}%20{str(self.end_Date)}%22%2C%22resolution%22%3A%22MONTH%22%2C%22locale%22%3A%22en-US%22%2C%22comparisonItem%22%3A%5B%7B%22geo%22%3A%7B%22country%22%3A%22US%22%7D%2C%22complexKeywordsRestriction%22%3A%7B%22keyword%22%3A%5B%7B%22type%22%3A%22BROAD%22%2C%22value%22%3A%22{self.keyword}%22%7D%5D%7D%7D%5D%2C%22requestOptions%22%3A%7B%22property%22%3A%22%22%2C%22backend%22%3A%22IZG%22%2C%22category%22%3A0%7D%7D&token={token}&tz=-120"

        self.monthly = pd.read_csv(url, header=1)
        self.monthly = self.monthly.rename(
            columns={"Month": "Date", f"{self.keyword}: (United States)": "relative_frequency"})

    def get_token(self, timespan):
        """
        Retrieves a token from Google Trends, based on the keyword and timespan.

        This function is a deritative of a function within Pytrends by github.com/GeneralMills.
        Licensed under the Apache license, version 2.0.
        Changes made by github.com/cristianpjensen to fit Njord's use case.
        """

        session = requests.session()

        response = session.get(
            url="https://trends.google.com/trends/api/explore",
            timeout=(2, 5),
            cookies=dict(filter(lambda i: i[0] == "NID", requests.get(
                "https://trends.google.com/?geo=US",
                timeout=(2, 5)
            ).cookies.items())),
            params={"hl": "en-US", "tz": -120,
                    "req": '{"comparisonItem": [{"keyword": ' + f'"{self.keyword}"' + ', "time": ' + f'"{timespan}"' + ', "geo": "US"}], "category": 0, "property": ""}'}
        )

        content = response.text[4:]
        return json.loads(content)["widgets"][0]["token"]

    def adjust_weekly(self):
        """
        Adjusts the weekly data, based on the monthly data.

        Puts in one data point - from the monthly data - per 5-year increment,
        and computes the data inbetween via the percentage change of the
        unadjusted weekly data.
        """

        print("Adjusting weekly data...")

        # 0's to 1's, because you can't divide by 0.
        self.monthly.replace(0, 1)
        self.weekly.replace(0, 1)

        self.weekly["percentage_change"] = \
            1 + self.weekly["relative_frequency"].pct_change()
        self.weekly["Adjusted"] = ""

        i = 0
        while True:
            try:
                self.weekly.loc[i * 261, "Adjusted"] = self.monthly.loc[i *
                                                                        60, "relative_frequency"]
                i += 1
            except:
                break

        for i in range(len(self.weekly)):
            if self.weekly["Adjusted"][i] == "":
                prc = float(self.weekly["percentage_change"][i])
                prev_value = float(self.weekly["Adjusted"][i-1])
                new_value = prev_value * prc
                self.weekly.loc[i, "Adjusted"] = new_value

        self.weekly["Adjusted"] = (
            self.weekly["Adjusted"] * 100 / self.weekly["Adjusted"].max()).astype("int32")

        self.weekly.drop(["relative_frequency", "percentage_change"],
                         axis=1).to_csv(f"data/weekly/{self.keyword}.csv", index=False)

    def adjust_daily(self):
        """
        Adjusts the daily data, based on the weekly data.

        Puts in one data point - from the weekly data - per 6-month increment,
        and computes the data inbetween via the percentage change of the
        unadjusted daily data.
        """

        print("Adjusting daily data...")
        self.daily = self.daily.replace(0, 1)
        self.daily["percentage_change"] = 1 + \
            self.daily["relative_frequency"].pct_change()
        self.daily["Adjusted"] = ""

        start_increment = self.start_date
        end_increment = start_increment + relativedelta(months=+6)
        end = self.end_date

        # Compute all values after the data point, within it's increment.
        i = 0
        while True:
            imported = False
            while True:
                if i >= len(self.daily):
                    break

                if not imported:
                    try:
                        self.daily.loc[i, "Adjusted"] = self.weekly["Adjusted"].where(
                            self.weekly["Date"] == str(start_increment)).dropna().values[0]
                        imported = True
                    except:
                        pass
                else:
                    prc = float(self.daily["percentage_change"][i])
                    prev_value = float(self.daily["Adjusted"][i-1])
                    new_value = prev_value * prc
                    self.daily.loc[i, "Adjusted"] = new_value

                start_increment += relativedelta(days=+1)
                i += 1

                if start_increment >= end_increment:
                    break

            start_increment = end_increment
            end_increment += relativedelta(months=+6)

            if start_increment > end:
                break

        # Compute all values before the data point, within it's increment.
        i = 0
        while True:
            if i >= len(self.daily) - 1:
                break

            if self.daily.loc[i, "Adjusted"] == "":
                j = 0
                while True:
                    if self.daily.loc[i+j, "Adjusted"] == "":
                        j += 1
                    else:
                        prc = float(self.daily["percentage_change"][i+j])
                        new_value = float(self.daily["Adjusted"][i+j])
                        prev_value = int(new_value / prc)
                        self.daily.loc[i+j-1, "Adjusted"] = prev_value

                        j -= 1

                    if j <= 0:
                        break

            i += 1

        self.daily = self.daily.drop(
            ["relative_frequency", "percentage_change"], axis=1)
        self.daily["Adjusted"] = self.daily["Adjusted"].astype("int32")
        self.daily["Adjusted"] = (
            self.daily["Adjusted"] * 100 / self.daily["Adjusted"].max()).astype("int32")

        self.daily.to_csv(f"data/daily/{self.keyword}.csv", index=False)


if __name__ == "__main__":
    Trends()
