import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

company = 'AAPL'
years = 5

# Getting the financial data
income_statements = requests.get(f"https://financialmodelingprep.com/api/v3/income-statement/{company}?limit={years}&apikey={api_key}").json()
balance_sheets = requests.get(f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?limit={years}&apikey={api_key}").json()
cash_flows = requests.get(f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{company}?limit={years}&apikey={api_key}").json()
company_profile = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{company}?apikey={api_key}").json()

# Getting the historical stock prices
stock_prices = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/{company}?apikey={api_key}").json()['historical'][-years*252:] # Approximate trading days in a year

# Preparing the date-price dictionary for the stock
price_movement = {datetime.strptime(price['date'], '%Y-%m-%d'): price['close'] for price in stock_prices}

#assumptions change based on the company you are analysing 
discount_rate = 0.05
growth_rate = 0.02

fcf_list = []
fcf_dict = {} # to store free cash flows and their dates
for i in range(years):
    income_statement = income_statements[i]
    balance_sheet = balance_sheets[i]
    cash_flow = cash_flows[i]

    net_income = income_statement['netIncome']
    interest_expense = income_statement['interestExpense'] if 'interestExpense' in income_statement else 0
    tax_rate = income_statement['incomeTaxExpense'] / income_statement['incomeBeforeTax'] if income_statement['incomeBeforeTax'] != 0 else 0
    depreciation_amortization = income_statement['depreciationAndAmortization']
    change_in_nwc = (balance_sheet['totalCurrentAssets'] - balance_sheet['totalCurrentLiabilities']) - \
                    (balance_sheets[i+1]['totalCurrentAssets'] - balance_sheets[i+1]['totalCurrentLiabilities'] if i < years-1 else 0)
    capex = cash_flow['capitalExpenditure']

    fcf = net_income + (1 - tax_rate) * interest_expense + depreciation_amortization - change_in_nwc - capex
    fcf_list.append(fcf)
    fcf_dict[datetime.strptime(income_statement['date'], '%Y-%m-%d')] = fcf
    print(f"Projected Free Cash Flow for year {i+1}: {fcf}")

terminal_value = fcf_list[-1] * (1 + growth_rate) / (discount_rate - growth_rate)
dcf = sum([fcf / ((1 + discount_rate) ** (i + 1)) for i, fcf in enumerate(fcf_list)]) + terminal_value / ((1 + discount_rate) ** years)

shares_outstanding = company_profile[0]['mktCap'] / company_profile[0]['price'] # market cap divided by share price
dcf_per_share = dcf / shares_outstanding


print("\nThe DCF value per share is:", dcf_per_share)

# Plotting free cash flows and share price
fig, ax1 = plt.subplots()

color = 'tab:blue'
ax1.set_xlabel('Date')
ax1.set_ylabel('Free Cash Flow', color=color)
ax1.plot_date(list(fcf_dict.keys()), list(fcf_dict.values()), 'o-', color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Share Price', color=color) 
ax2.plot_date(list(price_movement.keys()), list(price_movement.values()), 'o-', color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.show()

#this will graph the Stock FCF from historic and comparison with stock movement
print("\nThe DCF value per share is:", dcf_per_share)

# Plotting free cash flows only
plt.figure()
plt.plot_date(list(fcf_dict.keys()), list(fcf_dict.values()), 'o-')
plt.xlabel('Date')
plt.ylabel('Free Cash Flow')
plt.title(f'Free Cash Flow of {company} over {years} years')
plt.grid(True)
plt.show()

# Plotting free cash flows and share price
fig, ax1 = plt.subplots()

color = 'tab:blue'
ax1.set_xlabel('Date')
ax1.set_ylabel('Free Cash Flow', color=color)
ax1.plot_date(list(fcf_dict.keys()), list(fcf_dict.values()), 'o-', color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Share Price', color=color) 
ax2.plot_date(list(price_movement.keys()), list(price_movement.values()), 'o-', color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.show()


