-- tabulate unweighted and weighted number of filing units
select "unweighted count | weighted count (#m) of filing units";
select count(*),  -- unweighted count of filing units
       round(sum(s006)*1e-6,3) -- weighted count of filing units (#m)
from dump;

-- weighted count by filing status (MARS)
select "filing status (MARS) | weighted count of filing units";
select MARS, -- filing status
       round(sum(s006)*1e-6,3) -- weighted count of filing units (#m)
from dump
group by MARS;

-- tabulate weight of those with NEGATIVE marginal income tax rates
select "weighted count of those with NEGATIVE MTR";
select round(sum(s006)*1e-6,3) -- weighted count of filing units (#m)
from dump
where mtr_inctax < 0;

-- construct NON-NEGATIVE marginal income tax rate histogram with bin width 10
select "bin number | weighted count | mean NON-NEGATIVE MTR in bin";
select cast(round((mtr_inctax-5)/10) as int) as mtr_bin, -- histogram bin number
       round(sum(s006)*1e-6,3), -- weight count of filing units in bin (#m)
       -- weighted mean marginal income tax rate on taxpayer earnings in bin:
       round(sum(mtr_inctax*s006)/sum(s006),2)
from dump
where mtr_inctax >= 0 -- include only those with NON-NEGATIVE marginal tax rate
group by mtr_bin
order by mtr_bin;
