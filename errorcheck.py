from taxcalc import *

rec = Records('puf_ubi.csv', weights='WEIGHTS.csv')
pol = Policy()
calc = Calculator(records=rec, policy=pol)
ubi = {
    2014: {'_UBI3': [10000]}
}
rec2 = Records('puf_ubi.csv', weights='WEIGHTS.csv')
pol2 = Policy()
pol2.implement_reform(ubi)
calc2 = Calculator(records=rec2, policy=pol2)
calc.advance_to_year(2014)
calc2.advance_to_year(2014)
calc.calc_all()
calc2.calc_all()
print ((calc2.records._combined - calc.records._combined) * calc2.records.s006).sum()
