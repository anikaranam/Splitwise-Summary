import sys
import creds
import calendar
import matplotlib.pyplot as plt 
import numpy as np 
from datetime import datetime
import pandas as pd
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

from_date = sys.argv[1]
end_date = sys.argv[2]

def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

if (not is_valid_date(from_date)) or (not is_valid_date(end_date)):
	print('Please enter a valid start and end date')
	exit()
elif from_date > end_date:
	print('End date should be later than start date')
	exit()

from splitwise import Splitwise
spltwise_object = Splitwise(creds.consumer_key, creds.consumer_secret, api_key=creds.api_key)

class UserExpense:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, description, date, cost, category):
        self.description = description
        self.date = date
        self.cost = round(cost, 2)
        dateArray = date.split('-');
        self.year = dateArray[0]
        self.month = dateArray[1]
        self.category = category

    def __repr__(self) -> str:
        return self.description + ' on ' + self.date + ' for $' + str(self.cost)


current = spltwise_object.getCurrentUser()
print('Welcome ' + current.getFirstName() + ' ' + current.getLastName());

def getAllExpenses(from_date, end_date):
	expenses = spltwise_object.getExpenses(dated_after=from_date, dated_before=end_date, limit=100000)
	obj = []
	cost_array = []
	for exp in expenses:
		for users in exp.getUsers():
			if users.getFirstName() == 'Anirudh' and exp.getDescription() != 'Settle all balances':
				if float(users.getOwedShare()) > 0.0 and exp.getDescription() != 'Payment':
					obj.append(UserExpense(exp.getDescription(), exp.getDate(), float(users.getOwedShare()), exp.getCategory().getName()))
					cost_array.append(float(users.getOwedShare()))
	return obj, cost_array

def getTotalAmountSpent(all_expenses):
	total_owed = 0.0
	for exp in all_expenses:
		total_owed += exp.cost
	print('The sum of all your expenses is $' + str(round(total_owed, 2)))

def getMaxAmountSpent(all_expenses):
	max_cost = 0.0
	expDesc = None
	for exp in all_expenses:
		if exp.cost > max_cost:
			max_cost = exp.cost
			expDesc = exp
	print('Maximum amount spent is: ' + str(expDesc))

def getMinAmountSpent(all_expenses):
	min_cost = all_expenses[0].cost
	expDesc = all_expenses[0]
	for exp in all_expenses[1:]:
		if exp.cost < min_cost:
			min_cost = exp.cost
			expDesc = exp
	print('Minumum amount spent is: ' + str(expDesc))

def getAverageCost(cost_array):
	print('Average cost per expense is $' + str(round(sum(cost_array) / len(cost_array), 2)))

def plotExpenseChart(cost_array, from_date, end_date):
	y = np.array(cost_array)
	x = range(len(cost_array))  # Y-axis points 
	plt.xlabel("Expense number")  # add X-axis label 
	plt.ylabel("Cost of each expense")  # add Y-axis label 
	plt.title("Expenses from " + from_date + ' to ' + end_date)  # add title 
	plt.plot(x, y, zorder=3)  # Plot the chart 
	plt.grid(axis = 'y', zorder=0)
	plt.show()

def showExpensesByMonth(all_expenses):
	obj = {}
	for exp in all_expenses:
		key = exp.year + exp.month
		if key in obj:
			obj[key] += exp.cost
		else:
			obj[key] = exp.cost
	months = list(obj.keys())
	costs = list(obj.values())
	for i in range(len(months)):
		month = int(months[i][4:])
		months[i] = list(calendar.month_name)[month] + ' ' + str(months[i][:4])
	plt.bar(months, costs, color ='maroon', 
        width = 0.4, zorder=3)
	plt.grid(axis = 'y', zorder=0)
	plt.xlabel("Month")  # add X-axis label 
	plt.ylabel("Total expense (in $)")  # add Y-axis label 
	plt.title("Expenses per month")  # add title 
	plt.show()

def showExpensesByYear(all_expenses):
	obj = {}
	for exp in all_expenses:
		key = exp.year + exp.month
		if key in obj:
			obj[key] += exp.cost
		else:
			obj[key] = exp.cost
	months = list(obj.keys())
	costs = list(obj.values())
	for i in range(len(months)):
		month = int(months[i][4:])
		months[i] = list(calendar.month_name)[month] + ' ' + str(months[i][:4])
	plt.bar(months, costs, color ='maroon', 
        width = 0.4, zorder=3)
	plt.grid(axis = 'y', zorder=0)
	plt.xlabel("Month")  # add X-axis label 
	plt.ylabel("Total expense (in $)")  # add Y-axis label 
	plt.title("Total cost per month")  # add title 
	plt.show()

def showExpensesByCategory(all_expenses):
	obj = {}
	for exp in all_expenses:
		key = exp.category
		if key in obj:
			obj[key] += exp.cost
		else:
			obj[key] = exp.cost
	categories = list(obj.keys())
	costs = list(obj.values())
	plt.bar(categories, costs, color ='maroon', 
        width = 0.4, zorder=3)
	plt.grid(axis = 'y', zorder=0)
	plt.xlabel("Category")  # add X-axis label
	plt.ylabel("Total expense (in $)")  # add Y-axis label
	plt.title("Total cost per category")  # add title
	plt.show()

def showExpenseCountByCategory(all_expenses):
	obj = {}
	for exp in all_expenses:
		key = exp.category
		if key in obj:
			obj[key] += 1
		else:
			obj[key] = 1
	categories = list(obj.keys())
	costs = list(obj.values())
	plt.bar(categories, costs, color ='maroon', 
        width = 0.4, zorder=3)
	plt.grid(axis = 'y', zorder=0)
	plt.xlabel("Category")  # add X-axis label
	plt.ylabel("Number of expenses")  # add Y-axis label
	plt.title("Number of expenses per category")  # add title
	plt.show()

def findAnomalies(all_expenses):
	categories = []
	costs = []
	for exp in all_expenses:
		categories.append(exp.category)
		costs.append(exp.cost)
	categories = np.array(categories)
	label_encoder = LabelEncoder()
	categories_integer = label_encoder.fit_transform(categories)
	df = pd.DataFrame(list(zip(categories_integer, costs, categories)), columns=["Category-Int", "Expense", "Category"])
	print(df)
	model=IsolationForest(n_estimators=50, max_samples='auto', contamination=float(0.1),max_features=1.0)
	model.fit(df[['Category-Int', 'Expense']])

	df['scores']=model.decision_function(df[['Category-Int', 'Expense']])
	df['anomaly']=model.predict(df[['Category-Int', 'Expense']])
	print('Below are some unusual expenses based on the category of expense. Please review them:')
	print(df.loc[df['anomaly'] == -1, ["Category", "Expense"]])

def findExpensesPerCategory(all_expenses, category="General"):
	categories = []
	costs = []
	for exp in all_expenses:
		categories.append(exp.category)
		costs.append(exp.cost)
	df = pd.DataFrame(list(zip(categories, costs)), columns=["Category", "Expense"])
	print('Your expenses for the ' + category + ' category are:')
	print(df.loc[df['Category'] == category])

def findExpensePercentage(all_expenses, from_date, end_date):
	total_cost = 0.0
	categoryCosts = {}
	for exp in all_expenses:
		if from_date < exp.date < end_date:
			if not exp.category in categoryCosts:
				categoryCosts[exp.category] = exp.cost
			else:
				categoryCosts[exp.category] += exp.cost
			total_cost += exp.cost
	costs = np.array(list(categoryCosts.values())) / total_cost
	fig, ax = plt.subplots()
	ax.pie(costs, labels=list(categoryCosts.keys()), radius = 1.0)

all_expenses, cost_array = getAllExpenses(from_date, end_date)
getTotalAmountSpent(all_expenses)
getMaxAmountSpent(all_expenses)
getMinAmountSpent(all_expenses)
getAverageCost(cost_array)
plotExpenseChart(cost_array, from_date, end_date)
showExpensesByMonth(all_expenses)
showExpensesByCategory(all_expenses)
showExpenseCountByCategory(all_expenses)
findAnomalies(all_expenses)
findExpensesPerCategory(all_expenses)
findExpensePercentage(all_expenses, from_date, end_date)