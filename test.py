import pdb
import pickle
import pandas as pd
filename = 'data/onemonth_3152_0801.pkl'
with open(filename, 'rb') as fp:
	dataDict = pickle.load(fp)
data = pd.DataFrame.from_dict(dataDict)
data = data.drop(['Temp Occ Sts', 'Occupied Clg Min', 'Cooling Max Flow'], axis=1)



def discretize_temperature(data):
	for idx, datum in data.iterkv():
		data[idx] = round(datum)
	return data

def discretize_percentage(data):
	for idx, datum in data.iterkv():
		data[idx] = int(datum/10)
	return data

def discretize_flow(data):
	for idx, datum in data.iterkv():
		data[idx] = int(datum/100)
	return data

data['Zone Temperature'] = discretize_temperature(data['Zone Temperature'])
data['Actual Cooling Setpoint'] = discretize_temperature(data['Actual Cooling Setpoint'])
data['Common Setpoint'] = discretize_temperature(data['Common Setpoint'])
data['Actual Heating Setpoint'] = discretize_temperature(data['Actual Heating Setpoint'])
data['Warm Cool Adjust'] = discretize_temperature(data['Warm Cool Adjust'])

data['Heating Command'] = discretize_percentage(data['Heating Command'])
data['Cooling Command'] = discretize_percentage(data['Cooling Command'])
data['Damper Command'] = discretize_percentage(data['Damper Command'])

data['Actual Sup Flow SP'] = discretize_flow(data['Actual Sup Flow SP'])
data['Actual Supply Flow'] = discretize_flow(data['Actual Supply Flow'])

#data = datadrop(['Temp Occ Sts', 'Occupied Clg Min', 'Cooling Max Flow'], axis=1)


data  = data[['Common Setpoint', 'Actual Heating Setpoint', 'Occupied Command']]
data.to_excel(filename.replace('.pkl', '.xlsx'))
