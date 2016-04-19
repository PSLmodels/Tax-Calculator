%INCLUDE "taxcalc.sas";
proc import datafile="compare-in.csv" out=indata dbms=csv; getnames=yes;
run;
data outdata;
set indata;
%INIT;
_puf = 0; * the setting of _puf to 1 in the INIT macro may need to be skipped;
_numxtr = numextra;
_agep = 50;
_ages = 50;
if numextra ge 1 then _agep = 70;
if numextra ge 2 then _ages = 70;
%COMP;
_nbertax = _nbertax + c07200; * ignore Sch.R credit not in Tax-Calculator;
keep RECID c00100 c02500 c04600 c04470 c04800 c05200 c05800
     c07180 c07220 c09600 c11070 c21040 c59660 _nbertax;
proc export data=outdata outfile="compare-out.csv" dbms=csv replace;
run;
