from taxcalc import *
#Create a Parameters object
params = Parameters()
print(params.almdep)

#Create a Public Use File object
puf = PUF("puf2.csv")

#Create a Calculator
calc = Calculator(parameters=params, puf=puf)

#The Current Year is given from the Parameters and PUF objects
print(calc.current_year)

#Parameters that vary by year are scalars based on the current year
print(params.almdep)

#All the calculation happens through this interface
calc.calc_all()

#The year is incremented
calc.increment_year()

#The parameters scalars are updated, as is the PUF data
# (aging data by inflation)
print(params.almdep)

#Calculate again for the year
calc.calc_all()
