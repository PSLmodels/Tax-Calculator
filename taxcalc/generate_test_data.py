import pandas as pd
import numpy as np
from numpy.random import RandomState

# Set seed for reproducibility
state = RandomState(1789)

# read in test data which is just validation 'c' set from TAXSIM32
test_data = pd.read_csv('taxcalc_test_data.csv')

# Sample size
n = 100000

test_data['e87530'] = state.randint(0, 1e6+1, n)
test_data['e20100'] = state.randint(0, 1e6+1, n)
test_data['e07300'] = state.randint(0, 25000+1, n)
test_data['e03300'] = state.randint(0, 5000+1, n)
test_data['e09700'] = state.randint(0, 2+1, n) #?
test_data['e03230'] = state.randint(0, 100+1, n)
test_data['e27200'] = state.randint(0, 250000+1, n)
test_data['e03270'] = state.randint(0, 5000+1, n)
test_data['e07240'] = state.randint(0, 1000+1, n)
test_data['e03290'] = state.randint(0, 2000+1, n)
test_data['e58990'] = state.randint(0, 1e5+1, n)
test_data['e03240'] = state.randint(0, 5000+1, n)
test_data['e00400'] = state.randint(0, 25000+1, n)
test_data['e01100'] = state.randint(0, 2500+1, n)
test_data['e02100p'] = state.randint(0, 25000+1, n)
test_data['e24515'] = state.randint(0, 10000+1, n)
test_data['e03400'] = state.randint(0, 1000+1, n)
test_data['e17500'] = state.randint(0, 5000+1, n)
test_data['e03220'] = state.randint(0, 750+1, n)
test_data['e87521'] = state.randint(0, 300+1, n)
test_data['e03500'] = state.randint(0, 25000+1, n)
test_data['e09800'] = state.randint(0, 100+1, n)
test_data['e03150'] = state.randint(0, 2500+1, n)
test_data['e03210'] = state.randint(0, 1000+1, n)
test_data['e20400'] = state.randint(0, 10000+1, n)
test_data['e01200'] = state.randint(0, 1e6+1, n)
test_data['e09900'] = state.randint(0, 5000+1, n)
test_data['e11200'] = state.randint(0, 5000+1, n)
test_data['e01400'] = state.randint(0, 50000+1, n)
test_data['e24518'] = state.randint(0, 50000+1, n)
test_data['e07260'] = state.randint(0, 5000+1, n)
test_data['e00700'] = state.randint(0, 10000+1, n)
test_data['e62900'] = state.randint(0, 25000+1, n)
test_data['e07600'] = state.randint(0, 5000+1, n)
test_data['e19800'] = state.randint(0, 100000+1, n)
test_data['e07400'] = state.randint(0, 50000+1, n)

test_data['e02100s'] = state.randint(0, 5e5+1, n)
test_data['e02100p'] = state.randint(0, 5e5+1, n)
test_data['e02100s'] = state.randint(0, 5e5+1, n)
test_data['e02100p'] = state.randint(0, 5e5+1, n)
test_data['e00900s'] = state.randint(0, 5e5+1, n)
test_data['e00900p'] = state.randint(0, 5e5+1, n)


test_data['elderly_dependents'] = state.randint(0, 3+1, n)
test_data['cmbtp'] = state.randint(0, 1e6+1, n)
test_data['nu13'] = state.randint(0, 10+1, n)
test_data['g20500'] = state.randint(0, 65000+1, n)
test_data['n1820'] = state.randint(0, 3+1, n)
test_data['nu06'] = state.randint(0, 5+1, n)
test_data['DSI'] = state.randint(0, 1+1, n)
test_data['pencon_p'] = state.randint(0, 15000+1, n)
test_data['pencon_s'] = state.randint(0, 15000+1, n)
test_data['k1bx14s'] = state.randint(0, 4e6+1, n)
test_data['k1bx14p'] = state.randint(0, 4e6+1, n)
test_data['nu18'] = state.randint(0, 5+1, n)
test_data['s006'] = state.randint(0, 10+1, n)
test_data['n21'] = state.randint(0, 3+1, n)
test_data['MIDR'] = state.randint(0, 1+1, n)
test_data['f6251'] = state.randint(0, 1+1, n)
test_data['MARS'] = state.randint(1, 5+1, n)


# correcting errors from taxcalc
test_data['e02100s'] = np.where(test_data['MARS'] == (2 or 3), test_data['e02100s'], 0)
test_data['e00200s'] = np.where(test_data['MARS'] == (2 or 3), test_data['e00200s'], 0)
test_data['e00900s'] = np.where(test_data['MARS'] == (2 or 3), test_data['e00900s'], 0)
test_data['e02100'] = test_data['e02100p'] + test_data['e02100s']
test_data['e00200'] = test_data['e00200p'] + test_data['e00200s']
test_data['e00900'] = test_data['e00900p'] + test_data['e00900s']

test_data['k1bx14s'] = np.where(test_data['MARS'] == (2 or 3), test_data['k1bx14s'], 0)


test_data.to_csv('test_data.csv')



# weights
weights = pd.DataFrame()
for num, year in enumerate(range(2011, 2030+1)):
    weights['WT' + str(year)] = year + state.randint(0, 50+1, size = n) + num * 75

weights.to_csv('test_weights.csv')




# adjustment ratios
ratio_size = 20
ratios = pd.DataFrame()
for num, year in enumerate(range(2011, 2030+1)):
    ratios['INT' + str(year)] = state.uniform(0.75, 1.5, size=ratio_size)

ratios.T.to_csv('test_ratios.csv', index_label = 'agi_bin')
