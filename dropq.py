
# load input data

# load planX
planX_file_name = ''
with open(planX_file_name) as planX_file:
	planX = json.loads(planX_file.read())

# load planY
planY_file_name = ''
with open(planY_file_name) as planY_file:
	user_planY_dict = json.loads(planY_file.read())

print_different_params(planX, user_planY_dict)
# incorporate planY into planX
complete_planY = dict(planX, **user_planY_dict)

# one loop iteration (do this for every year)
# for every row in database:
# we take our data and age it a year to array djfo ?
# using this data we calculate tax1 using calc procedure
# add $1 to income element of djfo
# we calculate tax2 using calc procedure and modified djfo
# if tax2 != tax1, set records to active
# we calculate tax3 using tax2 and modified djfo
# pick 3 random active records and set them to zero

# return table of tax0

# return table of tax3 - tax1

# go to next row

## functions
def print_different_params(planX, user_planY):
	message = 'User passed different param "{param}". Default is {default}'
	for param in planY:
		if planX[param] != user_planY[param]:
			print message.format(param=param, default=planX[param])


## function stubs

def ohare(tax_payer_row, year):
	'''This function ages items in data by a year.
	Maybe a more expressive name would be nice for this.
	'''
	return year

def calculate_tax(tax_payer_row, year, plan):
	'''Actually, not very sure about this one. It's supposed to calculate
	tax and other variables for a given tax payer under the "plan".
	Not sure what year is doing here.
	As with previous function, details have not yet been fleshed out.
	'''
	return tax