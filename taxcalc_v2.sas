
/*
Taxcalc.sas is a calculator for the US Federal Income Tax 

It was written by Inna Shapiro (NBER) and Daniel Feenberg (NBER) with help from 
Micahel Strudler and Victoria Bryant of SOI. Users are asked to please
correspond with feenberg@nber.org after visiting the taxcalc website at
  
  http://www.nber.org/taxcalc 


Insole File Infelicities:

e07980 is used for electric vehicle and ny liberty zone
e07970 is used for rate reduction credit and electric vehicle credit
n11 is used for number of children and number of countries
e35210* and e35220* are used for non-dollar amounts
t35200 and t35300 seem to be the same concept
t35905 changes concept from income exclusion to sum of that and housing deduction
schj and schjin mean the same thing?
e03200 is jury duty pay deduction 2006 but primary IRA in 1994-1996
e09700 (recapture tax) is missing from datasets
e87662 is 1000 times fraction documented
advance rate reduction credit is not available
advance child tax credit is not available
e20200 combines cash and asset giving
*/

%MACRO _NOTICE;
 %PUT NOTE: TAXCALC version 111a (c) 2013 National Bureau of Economic Research;
 %PUT NOTE: Documentation at http://www.nber.org/taxcalc;
 %PUT NOTE: 102.1;
%MEND _NOTICE;
%_NOTICE;

%MACRO COMP;

If  1993>FLPDYR or FLPDYR>2013 then do;
  put "ER" "ROR: FLPDYR out of range for taxcalc: " FLPDYR= RECID= _n_=;
  stop;
end;

/* Factors for joint or separate filing */

if MARS eq 3 or MARS eq 6 then _sep = 2; else _sep = 1;
if MARS eq 2 or MARS eq 5 then _txp = 2; else _txp = 1;

/* Form 2555 */

if SOIYR eq 1993 then _feided = 0;                                     /*Don't have docs */
else if SOIYR eq 1994       then _feided = e35200 + e35500;
else if SOIYR eq 1995       then _feided = sum(e35200,e25500);
else if SOIYR eq 1996       then _feided = max(e35910+e35600,t35200);
else if SOIYR eq 1997       then _feided = max(t35200+t35500,t35200);
else if SOIYR in(1998:2000) then _feided = max(t34900+t35200-t35800+t35500,t35200);
else if SOIYR eq 2001       then _feided = max(e35800+e35200+e35500-e35800,0); /* 2555ez missing */
else if SOIYR in(2002,2003) then _feided = max(t34900+t35200-t35800+t35500,t35200);
else if SOIYR eq 2004       then _feided = max(t35800+t35200+t34900,t35200);
else if SOIYR in(2005,2006) then _feided = max(max(t35905+t35500,t35200),max(e35905+e35500,e35200));
else if SOIYR in(2007:2010) then _feided = max(t35905+t35500,t35200);
else if SOIYR ge 2011       then _feided = max(e35300_0,e35600_0+e35910_0);;

/* Adjustments */

c02900 = x03150 + e03210 + e03600 + e03260 + e03270 + e03300 
       + e03400 + e03500 + e03280 + e03900 + e04000 + e03700;

if SOIYR  eq 2006 then c02900 = c02900 + x03200; *Jury duty;
if FLPDYR ge 2002 then c02900 = c02900 + e03220 + e03230;
if FLPDYR ge 2005 then c02900 = c02900 + e03240;
if FLPDYR ge 2004 then c02900 = c02900 + e03290;
x02900 = c02900;

/* Capital Gains */

c23650 = e23250 + e22250;
if FLPDYR ge 1994 then c23650 = c23650 + e23660;
c01000 = max(-3000/_sep,c23650);

c02700 = min(_feided,_feimax{FLPDYR}*F2555);

/* _ymod is income less adjustments plus half of SS benefits */

_ymod1 = e00200 + e00300 + e00600 + e00700 + e00800 + e00900 
       + c01000 + e01100 + e01200 + e01400 + e01700 + e02000 
       + e02100 + e02300 + e02600 + e02610 + e02800 - e02540;
_ymod2 = e00400 + e02400/2 - c02900;
_ymod3 = 0;
if FLPDYR gt 1998 then _ymod3 = _ymod3 + e03210;
if FLPDYR ge 2002 then _ymod3 = _ymod3 + e03230;
if FLPDYR gt 2009 then _ymod3 = _ymod3 + e02615;
if FLPDYR ge 2005 then _ymod3 = _ymod3 + e03240;
_ymod = _ymod1 + _ymod2 + _ymod3;

/* Taxation of Social Security Benefits*/

if SSIND ne 0 or MARS in(3,6) then  /* Can't calculate these w/o more info */
   c02500 = e02500; 
else if _ymod lt _ssb50(MARS) then
   c02500 = 0;
else if FLPDYR eq 1993 or (_ymod ge _ssb50(MARS) and _ymod lt _ssb85(MARS)) then
   c02500 = .5*min(_ymod-_ssb50(MARS),e02400);
else
   c02500 = min(.85*(_ymod-_ssb85(MARS))
          +  .50*min(e02400,_ssb85(MARS)-_ssb50(MARS)),
            .85*e02400);

/* Gross Income */

c02650 = _ymod1 + c02500 - c02700;
if FLPDYR ge 2010 then c02650 = c02650 + e02615;

/* AGI */

c00100  = c02650 - c02900;
_agierr = e00100 - c00100;        
if _fixup ge 1 then c00100 = c00100+_agierr;
_posagi  = max(c00100,0);
_ywossbe = e00100 - e02500;
_ywossbc = c00100 - c02500;

/* Personal Exemptions  (_phaseout smoothed) */

if FLPDYR in(2005:2009) then _katrina=min(N11*500,2000);
_prexmp = xtot*_amex{FLPDYR};
if FLPDYR in(2005:2009) then _prexmp = _prexmp+_katrina;
if _exact then do
  _ratio = (_posagi - _exmpb{FLPDYR,MARS})/(2500/_sep);
  _tratio = CEIL(_ratio);
  _dispc  = min(1,max(0,.02*_tratio));
end;
else do;
  _dispc  = min(1,max(0,.02*(_posagi-_exmpb{FLPDYR,MARS})/(2500/_sep)));
end;
_flpdym = 100*FLPDYR + FLPDMO;
if _flpdym ge 200612 and _flpdym le 200811 then _dispc = (2./3.)*_dispc;
if _flpdym ge 200812 and _flpdym le 201011 then _dispc = (1./3.)*_dispc;
if _flpdym ge 201012 and _flpdym le 201212 then _dispc = 0; 
c04600 = _prexmp*(1-_dispc);   

/* Itemized Deductions */

/* Medical */
c17750 = .075*_posagi;             
c17000 =  max(0,e17500-c17750);
xx=2;

/* State and local income tax, or sales tax */
_sit = max(e18400,e18425,0);
if FLPDYR ge 2004 then
   _statax = max(_sit,e18450);
else
   _statax = _sit;

/* Other Taxes */
c18300 = _statax + e18500 + e18800 + e18900;  
if FLPDYR in(2009,2010) and _statax ge e18450 then c18300 = c18300 + e18600;

/* Casulty */
if e20500 gt 0 then do;
  c37703 = e20500+.1*_posagi;
  c20500 = c37703-.1*_posagi;     
end;
else do;
  c37703 = 0;
  c20500 = 0;
end;

/* Misc */
c20750 = .02*_posagi;           
if _puf then do;
  c20400 = e20400;
  c19200 = e19200;
end;
else do;
  c20400 = e20550 + e20600 + e20950;
  c19200 = e19500 + e19530 + e19570 + e19400 + e19550;
end;
c20800 = max(0.,c20400-c20750);

/* Charity (Assumes carryover is non-cash) */
if e19800 + e20100 + e20200 le .2*_posagi then
  c19700 = e19800 + e20100 + e20200;
else do;
  _lim50 = min(.5*_posagi,e19800);
  _lim30 = min(.3*_posagi,e20100 + e20200);    
  c19700 = min(.5*_posagi,_lim30 + _lim50);
end;

/* Gross Itemized Deductions */

c21060 = e20900 + c17000 + c18300 + c19200 
       + c19700 + c20500 + c20800 + e21000 + e21010;

if FLPDYR le 1994 then c21060 = c21060 + e20300;

/* Itemized Deduction Limitation */

c04470 = c21060 ;  
if FLPDYR lt 2013 then 
  _phase2 = _phase{FLPDYR};
else do;
   _phase2 = 300000;
   if MARS eq 1 then _phase2 = 200000;
   else if MARS eq 4 then _phase2 = 250000;
end;

_itemlimit=1;
_c21060 = c21060;
_nonlimited = c17000 + c20500 + e19570 + e21010 + e20900;
_limitratio = _phase2/_sep;
if c21060 gt _nonlimited and FLPDYR ge 1991 and c00100 gt _phase2/_sep then do;
     _itemlimit=2;
    _dedmin = .8*(c21060-_nonlimited);
    _dedpho = .03*max(0,_posagi-_phase2/_sep);
    c21040 = min(_dedmin,_dedpho);
    if FLPDYR eq 2006 or  FLPDYR eq 2007 then c21040 = (2/3)*c21040;
    if FLPDYR eq 2008 or  FLPDYR eq 2009 then c21040 = (1/3)*c21040;
    if FLPDYR ge 2010 and FLPDYR le 2012 then c21040 = 0;
    c04470 = c21060 - c21040;            
end;
else do;
    c21040 = 0;
end;

/* Earned income and FICA */

_sey    = e00900 + e02100;
_fica   = max(0,.153*min(_ssmax(FLPDYR),e00200+max(0,_sey)*.9235));
_setax  = max(0,_fica - .153*e00200);
if _setax le 14204 then  /*XXX where does 14204 come from?*/
  _seyoff = .5751*_setax;
else
  _seyoff = .5*_setax + 10067;

if FLPDYR GE 2004 then c11055 = e11055; else c11055 = 0;
_earned = max(0,e00200 + e00250 + e11055 + e30100 + _sey - _seyoff);

/*Standard Deduction with Aged, Sched L and Real Estate*/

if DSI eq 1 then do;
   if FLPDYR lt 1998 then 
      c15100 = max(_earned,_stded(FLPDYR,7));
   else if FLPDYR ge 1998 and FLPDYR le 2005 then 
      c15100 = max(250+_earned,_stded{FLPDYR,7});
   else 
      c15100 = max(300+_earned,_stded{FLPDYR,7});

   c04100 = min(_stded{FLPDYR,MARS},c15100);
end;
else do;
  if _compitem OR (mars in(3,6) and MIDR) then
    c04100 = 0;
  else
    c04100 = _stded{FLPDYR,MARS}; 
end;

if FLPDYR ge 2009 then c04100 = c04100 + e15360;
if FLPDYR eq 2008 or FLPDYR eq 2009 then do;
  if _puf then _rltaxsd = e18500; else _rltaxsd = e04250;
  c04250 = min(_rltaxsd,_txp*500);
  c15250 = c04250;
end;

_numextra = AGEP + AGES + PBI + SBI;
if MARS eq 2 or MARS eq 3 or MARS eq 6 then _txpyers = 2; else _txpyers = 1;
c04200 = _numextra*_aged(_txpyers,FLPDYR);
if _exact and (MARS eq 3 or MARS eq 5) then c04200 = e04200;

c15200 = c04200;
_standard = c04100 + c04200;
if FLPDYR eq 2008 or FLPDYR eq 2009 then _standard = _standard + c04250;

if (MARS eq 3 or MARS eq 6) and c04470 gt 0 then _standard = 0;
if fded eq 1 then do;
  if soiyr eq 1998 then _othded = e04100 - c04470;else
  _othded = e04470 - c04470;
  if _fixup ge 2 then c04470 = c04470 + _othded;
  c04100 = 0;
  c04200 = 0;
  _standard = 0;
end;

c04500 = c00100 - max((c21060-c21040),c04100,_standard+e37717);
c04800 = max(0,c04500-c04600-e04805);
if _standard>0 then do;
   c60000 = c00100;  
   if FLPDYR le 2001 then c60000 = c60000 - c04100 - c04200;
    end;
else
   c60000 = c04500;

if FLPDYR in(2005,2009) then c60000 = c60000 - _katrina;
if FLPDYR ge 2008 then c60000 = c60000 - e04805;

/*Some taxpayers itemize only for AMT, not regular tax */
if FLPDYR le 2002 then _amtstd = _standard; else _amtstd = 0;
if e04470 eq 0 and t04470 gt _amtstd and f6251 eq 1 and _exact then c60000 = c00100 - t04470;

if FLPDYR GE 2006 and c04800 gt 0 and _feided gt 0 then do;
  _taxinc = c04800 + c02700;
  %TAXER(_feided,_feitax,MARS);
  %TAXER(c04800,_oldfei,MARS);
  end;
else do;
  _taxinc = c04800;
  _feitax = 0;
end;

/* Tax calculated with X, Y or Z and Schedule D*/

%TAXER(_taxinc,_xyztax,MARS);
%TAXER(c04800,c05200,MARS);
c24516 = max(0,min(e23250,c23650)) + e01100;
c24580 = _xyztax;

/* Tax on non-gain income */

_cglong = min(c23650,e23250) + e01100;
/*if _taxinc gt _brk3{FLPDYR,MARS} and
   ((FLPDYR in(1994:1996) and _cglong - sum(0,e58990) gt 0)
   or (FLPDYR eq 1993 and _taxinc gt c24516)) then do; */
if _taxinc gt _brk3{FLPDYR,MARS} and FLPDYR in(1993:1996) and _cglong gt 0 then do;
      _noncg = max(_brk2{FLPDYR,MARS},_taxinc - (_cglong - sum(0,e58990)));
      %TAXER(_noncg,c06300,MARS);
      _taxltg = .28*(_taxinc - _noncg);           /* tax on cg TI */
      c24580 = min(_taxltg + c06300,_xyztax);
end;
else
   _noncg = 0;

/* Tax with gains */
c24517=0;
c24520=0;
c24530=0;
c24533=0;
c24540=0;
c24581=0;
_dwks16=0;

_hasgain = e01000 gt 0 or c23650 gt 0 or e23250 gt 0 or e01100 gt 0;
if FLPDYR ge 2003 then _hasgain = _hasgain or e00650 gt 0;
if FLPDYR in(1997:2002) & _hasgain then do;
     c24510 = max(0,min(c23650,e23250)+e01100);         /* schD gain for tax comp */
     c24516 = max(0,c24510 - e58990);            /* gain less invest income */
     _dwks6 =  max(0,min(e22250+e22550 ,e22550));
     _dwks8 = _dwks6 + sum(e24515,0);            /* unrecaptured 1250 gain */
     c24517 = max(0,c24516 - _dwks8);            /* gain less 25% income */
     c24520 = max(0,c04800 - c24517);            /* tent TI less schD gain */
     c24530 = min(_brk2(FLPDYR,MARS),_taxinc);   /*min TI for bracket*/
     _dwks12 = min(c24520,c24530);
     _dwks13 = max(0,_taxinc - c24516);
     c24540 = max(_dwks12,_dwks13);
      %TAXER(c24540,c24560,MARS);                     /* e24560 non-SchD Tax */
     _dwks16 = c24530 - _dwks12;
     c24581 = _dwks16;
     if FLPDYR ge 2001 then do;
        _dwks17 = sum(e24583,0);
        c24585 = max(0,min(c24581,_dwks17));
        c24587 = .08 * c24585;                   /* SchD 8% Tax Amount */
        c24590 = c24581 - c24585;
     end;
     if FLPDYR le 2000 then c24590 = c24530 - _dwks12;
     c24595 = .1 * c24590;                    /* SchD 10% Tax Amount    */
     _dwks22 = min(_taxinc,c24517);
     if FLPDYR ge 2001 then
        c24600 = _dwks22 - c24581;           /* 20% SchD gains */
     else
        c24600 = _dwks22 - c24590;

     c24605 = .20 * c24600;                   /* Tax on 20% gains */
     _dwks26 = min(c24516,sum(e24515,0));
     _dwks27 = c24516 + c24540;
     _dwks29 = max(0,_dwks27-_taxinc);
     c24610 = max(0,_dwks26-_dwks29);         /* 25% SchD gains */
     c24615 = .25 * c24610;                   /* Tax on 25% gains */

     if FLPDYR ge 2001 then                   /* SchD 28% income */
        c24550 = _taxinc - (c24540 + c24581 + c24600 + c24610);
     if FLPDYR le 2000 then                 
        c24550 = _taxinc - (c24540 + c24590 +c24600 + c24610);
     c24570 = .28 * c24550;                   /* SchD 28% Tax */

     _taxspecial = c24595 + c24605 + c24615 + c24570 +c24560;
     if FLPDYR ge 2001 then _taxspecial = c24587 + _taxspecial;
     c24580 = min(_taxspecial,_xyztax);      /* SchD tax  */
end;

c24532 = 0;
if FLPDYR ge 2003 and _taxinc gt 0 and _hasgain then do;
   _dwks5 = max(0,sum(e58990,-sum(e58980,0)));
   c24505 = max(0,c00650 - _dwks5); 
   c24510 = max(0,min(c23650,e23250)) + e01100;      /* gain for tax computation */
   if e01100 gt 0 then c24510 = e01100;      /* from app f 2008 drf */
   _dwks9 = max(0,c24510-min(e58990,e58980));/* e24516 gain less invest y */
   c24516 = c24505 + _dwks9;
   _dwks12 = min(_dwks9,sum(e24515,e24518,0));
   c24517 = c24516 - _dwks12;                /* gain less 25% and 28%  */
   c24520 = max(0,_taxinc - c24517);         /* tentative TI less schD gain */
   c24530 = min(_brk2(FLPDYR,MARS),_taxinc); /* minimum TIfor bracket */
   _dwks16 = min(c24520,c24530);
   _dwks17 = max(0,_taxinc - c24516);
   c24540 = max(_dwks16,_dwks17);
   if FLPDYR eq 2003 then do;
      c24532 = c24530 - _dwks16;            /* 5% limitation amount   */
      c22256 = -min(0,sum(e21606,e21626,e21776,0));   /* net STL (5/5/03)*/
      c22556 = sum(e22306,e22326,e22366,e22376,0);    /* LTG or loss (5/5/03) */
      c23656 = max(0,-c22256 + c22556);     /* net capital gain before exclusion/loss limitation (5/5/03) */
      c24533 = c23656 + c24505;             /* qualifying dividend and schD gain (5/5/03)  */
      c24534 = min(c24532,c24533);          /* income subject to 5% tax */
   end;

   if FLPDYR ge 2004 then c24534 = c24530 - _dwks16;
   if FLPDYR LT 2008 then c24535 = .05 * c24534; else c24535 = 0; *e24535 Schedule D 5% Tax Amount;

   if FLPDYR eq 2003  then do;
      c24581 = c24532 - c24534;
      c24585 = min(c24581,sum(e24583,0));  /* income subject to 8% tax  */
      c24587 = .08 * c24585;               /* 8% Tax */
      c24590 = c24581 - c24585;            /* income subject to 10% tax  */
      c24595 = .1 * c24590;                /* 10% Tax */
      _dwks29 = min(_taxinc,c24517);
      _dwks31 = max(0,_dwks29-c24532);
      _dwks34 = c24533 - c24534;
      c24597 = min(_dwks31,_dwks34);       /* income subject to 15% tax  */
      c24598 = .15 * c24597;               /* 15% Tax Amount */
      c24600 = _dwks31 - c24597;           /* income subject to 20% tax */
      c24605 = .2 * c24600;                /* 20% Tax */
      _dwks39 = min(c24516,sum(e24515,0));
      _dwks40 = c24516 + c24540;
      _dwks42 = max(0,_dwks40-_taxinc);
      c24610 = max(0,_dwks39-_dwks42);     /* income subject to 25% tax */
      c24615 = .25 * c24610;               /* 25% Tax */
     _dwks45 = c24540+c24532+_dwks31+c24610;
      c24550 = max(0,_taxinc - _dwks45);          /* income subject to 28% tax */
      c24570 = .28 * c24550;               /* 28% Tax */
   end;
   if FLPDYR ge 2004  then do;
      _dwks21 = min(_taxinc,c24517);
      c24597 = max(0,_dwks21-c24534);      /* income subject to 15% tax */
      c24598 = .15 * c24597;               /* 15% Tax */
      _dwks25 = min(_dwks9,sum(e24515,0));
      _dwks26 = c24516 + c24540;
      _dwks28 = max(0,_dwks26-_taxinc);
      c24610 = max(0,_dwks25-_dwks28);     /* income subject to 25% tax*/
      c24615 = .25 * c24610;               /* 25% Tax */
      _dwks31 = c24540 + c24534 + c24597 + c24610;
      c24550 = max(0,_taxinc - _dwks31);          /* income subject to 28% tax */
      c24570 = .28 * c24550;               /* 28% Tax */
      if FLPDYR eq 2013  then do;
         if c24540 gt _brk6{FLPDYR,MARS} then 
            _addtax = .05*c24517;
         else if _taxinc gt _brk6{FLPDYR,MARS} then 
            _addtax = .05*min(c04800-_brk6{FLPDYR,MARS},c24517);
         else 
            _addtax = 0;

      end; 
   end;

   %TAXER(c24540,c24560,MARS);            /* e24560 non-Schedule D Tax Amount */
   _taxspecial = c24535 + c24598 + c24615 + c24570 + c24560;
   if FLPDYR eq 2013 then _taxspecial = _taxspecial + _addtax;
   if FLPDYR eq 2003 then _taxspecial = c24587 + c24595 + c24605 + _taxspecial;
   c24580 = min(_taxspecial,_xyztax);     /* e24580 schedule D tax  */
end;

c05100 = c24580;
if c04800 gt 0 and _feided gt 0 then c05100 = max(0,c05100-_feitax);

/* Form 4972 - Lump Sum Distributions */
  c05700 = 0;
if _cmp then do;
  c59430 = max(0,e59410-e59420);
  c59450 = c59430 + e59440;               /* Income plus lump sum */
  c59460 = max(0,min(.5*c59450,10000) - .2*max(0,c59450 - 20000));
  _line17 = c59450 - c59460;
  _line19 = c59450 - c59460 - e59470;
  _line22 = 0;
  if c59450 gt 0 then _line22 = max(0,e59440 - e59440*c59460/c59450);
 
/*tax savings from 5 year option years before 2000 */
  if FLPDYR le 1999 then do;
     _line23 = .2*(c59450 - c59460 - e59470);
     %TAXER(_line23,_line24,1)
     _line25 = 5*_line24;
     if e59440 eq 0 then 
        _line29 = _line25; 
     else if e59440 gt 0 then do;
        _line26 = .2*_line22;
        %TAXER(_line26,_line27,1)
        _line28 = 5*_line27;
        _line29 = max(0,_line25-_line28);
     end;
     c59485 = _line29;
  end;
 
  if (AGEP + AGES gt 0 and FLPDYR le 1999) or FLPDYR ge 2000 then do;
/*tax savings from 10 year option */
    _line30 = .1*max(0,(c59450 - c59460 - e59470));
    _line31=
   .11 * min(_line30,1190) /*Tax on income + lump sum*/
+  .12 * min ( 2270- 1190,max(0,_line30- 1190))
+  .14 * min ( 4530- 2270,max(0,_line30- 2270))
+  .15 * min ( 6690- 4530,max(0,_line30- 4530))
+  .16 * min ( 9170- 6690,max(0,_line30- 6690))
+  .18 * min (11440- 9170,max(0,_line30- 9170))
+  .20 * min (13710-11440,max(0,_line30-11440))
+  .23 * min (17160-13710,max(0,_line30-13710))
+  .26 * min (22880-17160,max(0,_line30-17160))
+  .30 * min (28600-22880,max(0,_line30-22880))
+  .34 * min (34320-28600,max(0,_line30-28600))
+  .38 * min (42300-34320,max(0,_line30-34320))
+  .42 * min (57190-42300,max(0,_line30-42300))
+  .48 * min (85790-57190,max(0,_line30-57190))
+  .50 * max(0,_line30-85790);
    _line32 = 10*_line31;
    if e59440 eq 0 then 
       _line36 = _line32; 
    else if e59440 gt 0 then do;
       _line33 = .1*_line22;
       _line34 = 
   .11 * min(_line33,1190) /*Tax on income + lump sum*/
+  .12 * min ( 2270- 1190,max(0,_line33- 1190))
+  .14 * min ( 4530- 2270,max(0,_line33- 2270))
+  .15 * min ( 6690- 4530,max(0,_line33- 4530))
+  .16 * min ( 9170- 6690,max(0,_line33- 6690))
+  .18 * min (11440- 9170,max(0,_line33- 9170))
+  .20 * min (13710-11440,max(0,_line33-11440))
+  .23 * min (17160-13710,max(0,_line33-13710))
+  .26 * min (22880-17160,max(0,_line33-17160))
+  .30 * min (28600-22880,max(0,_line33-22880))
+  .34 * min (34320-28600,max(0,_line33-28600))
+  .38 * min (42300-34320,max(0,_line33-34320))
+  .42 * min (57190-42300,max(0,_line33-42300))
+  .48 * min (85790-57190,max(0,_line33-57190))
+  .50 * max(0,_line33-85790);
       _line35 = 10*_line34;
       _line36 = max(0,_line32-_line35);  /*tax saving from 10 year option */
    end;
    if FLPDYR le 1999 then
       c59485 = min(c59485,_line36);
    else
       c59485 = _line36;
  end;
  c59490 = c59485 + .2*max(0,e59400);  /* pension gains tax plus */
  c05700 = c59490;
end;

if FLPDYR GE 2011 then _s1291 = e10105; else _s1291 = 0;
if FLPDYR GE 2011 then _parents = e83200_0; else _parents = e84200;
c05750 = max(sum(c05100,_parents,c05700/*,_s1291*/),sum(e74400));
_taxbc = c05750 ;*+ _feiexcgt;
x05750=c05750;

/* Additional Medicare tax on unearned Income */
if FLPDYR eq 2013 and c00100 gt _thresx{MARS} then 
 c05750 = c05750+
    .038*min(e00300+e00600+max(0,c01000)+max(0,e02000),c00100-_thresx{MARS});

/* Alternative Minimum Taxable Income */

c62720 = c24517 + x62720;
c60260 = e00700 + x60260;
if FLPDYR ge 1994 then c63100 = max(0,_taxbc-sum(e07300)); else c63100 = max(0,_taxbc);
c60200 = min(c17000,.025*_posagi);
c60240 = c18300 + x60240;
if FLPDYR in(2009,2010) and _statax ge e18450 then c60240 = c60240 - e18600;
c60220 = c20800 + x60220;
c60130 = c21040 + x60130;
c62730 = sum(e24515,x62730);
 
_amtded = c60200+c60220+c60240;
if c60000 le 0 then _amtded = max(0,_amtded + c60000);
if _standard eq 0 or (_exact and _amtded + e60290 gt 0) then 
   _addamt = _amtded + e60290 - c60130;
else do;
   if FLPDYR lt 2002 then _addamt = c04100 + c04200;
   if FLPDYR ge 2002 then _addamt = 0;
end;

if _cmp and FLPDYR ge 2002 then do;
   c62100 = _addamt + e60300 + e60860 + e60100 + e60840 + e60630
          + e60550  + e60720 + e60430 + e60500 + e60340 + e60680 + e60600 
          + e60405  + e60440 + e60420 + e60410 + e61400 + e60660 
          - c60260  - e60480 - e62000 +c60000;
   if FLPDYR ge 2008 then c62100 = c62100 - e60250;
end;
 
if _cmp and FLPDYR lt 2002 then do;
   _totadp = _addamt  - e60260 + e60300 + e60340 + e60500 + e60550  
             + e60680 + e60720 + e60840 + e60405 + e60860 + e60900 
             + e60480 + e61400 + e60430 + e60440 + e60600 + e60420 
             + e60620 + e60460 + e60410 + e60630 + e60640 + e60660 
             - e60480;
   if FLPDYR in(94:97) then _totadp = _totadp + e20200;
   if FLPDYR lt 1998   then _totadp = _totadp + c19700 + x60820;
   c62100 = c60000 + _totadp + e60100 - e62000;
end;

_cmbtp = 0;
if _puf and FLPDYR ge 2002 then do;
   if _standard eq 0 or (_exact and e04470 gt 0) then do;
      _edical = max(0,e17500 - max(0,e00100)*.075);
      if  f6251 then _cmbtp = - min(_edical,.025*max(0,e00100)) 
                           + e62100 + c60260 + e04470 + e21040
                           - _sit  - e00100 - e18500 - e20800;
      c62100 = c00100 - c04470 + min(c17000,.025*max(0,c00100))+ _sit  
             + e18500 - c60260 + c20800 - c21040 + _cmbtp ;
   end;
   if _standard>0 then do;
      if f6251 then _cmbtp = e62100 - e00100 + c60260;
      c62100 = c00100 - c60260 + _cmbtp;
   end;
end;

if _puf and FLPDYR lt 2002 then do;
   if _standard eq 0 or (_exact and e04470 gt 0) then 
      c62100 = min(c17000,.025*max(0,c00100)) + e61850 
             + e60100 - c60260 + c00100 - c04470 - c21040;
   else
      c62100 = c00100 + e61850 + e60100 - c60260;
end;
x62100 = c62100;
if MARS eq 3 or MARS eq 6 and c62100 gt _amtsep{FLPDYR} then do;
   _amtsepadd = max(0,min(_almsep(FLPDYR),.25*(c62100-_amtsep{FLPDYR})));
   c62100 = c62100 + _amtsepadd;
end;

c62600 = max(0,_amtex{FLPDYR,MARS} - .25*max(0,c62100 - _amtys{MARS},0));

if  _DOBYR gt 0 then   _agep = ceil((12*(FLPDYR -  _DOBYR) -  DOBMD/100)/12);
if _SDOBYR gt 0 then   _ages = ceil((12*(FLPDYR - _SDOBYR) - SDOBMD/100)/12);

if _cmp then do;
   if F6251 eq 1 and _exact then 
      c62600 = e62600;
   else if FLPDYR ge 1998 and _agep lt _amtage{FLPDYR} and _agep ne 0 then  
      c62600 = min(c62600,_earned + _almdep{FLPDYR});
end;

c62700= max(0, c62100 - c62600);

_alminc = c62700;
_amtfei = 0;
if c02700 gt 0 and FLPDYR GE 2006 then do;
   _alminc = max(0,c62100 - c62600 + c02700);
   _amtfei = .26*c02700 + .02*max(0,c02700 - _almsp{FLPDYR}/_sep);
end;
 
c62780 = .26*_alminc + .02*max(0,_alminc - _almsp{FLPDYR}/_sep)-_amtfei;
if f6251 ne 0 then c62900 = e62900; else c62900 = sum(e07300);
c63000 = c62780 - c62900;

c62740 = min(max(0,c24516+x62740),c62720+c62730);
if c24516 eq 0 then c62740 = c62720+c62730;


if FLPDYR le 2001 then 
   _ngamty = max(0,_alminc-min(c62740,c62730+c62720));
else
   _ngamty = max(0,_alminc-c62740);

c62745= .26*_ngamty + .02*max(0,_ngamty-_almsp{FLPDYR}/_sep);
y62745 = _almsp{flpdyr}/_sep;
_tamt2 = 0;

if FLPDYR in(1997:2000) then do;
   _amt10pc = min(max(0,_brk2(FLPDYR,MARS)-c24520),
              min(_alminc,c62720));
   _amt10pc = min(_alminc,c62720,c24590);
   c62750  =  _cgrate1(FLPDYR)*_amt10pc;
   _amt20pc = min(_alminc,c62720)-_amt10pc;
   _amt25pc = max(0,_alminc-_ngamty - _amt10pc - _amt20pc);
   c62760  = _cgrate2(FLPDYR)*_amt20pc;
   c62770  = .25*_amt25pc;
   _tamt2  = c62750 + c62760 + c62770;
end;
if FLPDYR in(2001:2002) and 0 then do;
  if min(e24581,min(_alminc,c62720)) eq 0 then do;
     c62749 = 0;
     c62750 = 0;
    end;
  else do;
     _amt8pc = min(min(e24581,min(_alminc,c62720)),e62748);
    c62749 = .08*_amt8pc;
    _amt10pc = min(e24581,min(_alminc,c62720)) - _amt8pc;
    c62750 = _cgrate1(FLPDYR)*_amt10pc;
  end; 
  _amt20pc = min(_alminc,c62720) - min(e24581,min(_alminc,c62720)); 
  c62760  = _cgrate2(FLPDYR)*_amt20pc;
  _amt25pc = max(0,min(_alminc,c62740) - min(_alminc,c62720));
  c62770  = .25*_amt25pc;
  _tamt2  = c62749 + c62750 + c62760 + c62770;
end;

if FLPDYR in(2001:2002) then do;
  if min(c24581,min(_alminc,c62720)) eq 0 then do;
     c62749 = 0;
     c62750 = 0;
    end;
  else do;
     _amt8pc = min(min(c24581,min(_alminc,c62720)),e62748);
    c62749 = .08*_amt8pc;
    _amt10pc = min(c24581,min(_alminc,c62720)) - _amt8pc;
    c62750 = _cgrate1(FLPDYR)*_amt10pc;
  end; 
  _amt20pc = min(_alminc,c62720) - min(c24581,min(_alminc,c62720)); 
  c62760  = _cgrate2(FLPDYR)*_amt20pc;
  if FLPDYR eq 2002 then
     _amt25pc = max(0,min(_alminc,c62740) - min(_alminc,c62720));
  else if FLPDYR eq 2001 then 
     _amt25pc = _alminc - (_ngamty + min(_alminc,c62720,c24581)+_amt20pc);
  c62770  = .25*_amt25pc;
  _tamt2  = c62749 + c62750 + c62760 + c62770;
end;
 
if FLPDYR ge 2004 then do;
   if FLPDYR ge 2008 then do;
      _amt5pc  = 0;
      _amt15pc = min(_alminc,c62720)-_amt5pc-min(max(0,_brk2(FLPDYR,MARS)
               -c24520),min(_alminc,c62720));
      if c04800 eq 0 then 
         _amt15pc = max(0,min(_alminc,c62720)-_brk2(FLPDYR,MARS));
      _amt25pc = min(_alminc,c62740) - min(_alminc,c62720);
   end;
   else do;
      _amt5pc = min(max(0,_brk2(FLPDYR,MARS)-c24520),min(_alminc,c62720));
      _amt15pc = min(_alminc,c62720) - _amt5pc;
      _amt25pc = max(0,_alminc-_ngamty - _amt5pc - _amt15pc);
   end;
   if c62730 eq 0 then _amt25pc = 0;
   c62747  =   _cgrate1(FLPDYR)*_amt5pc;
   c62755  =   _cgrate2(FLPDYR)*_amt15pc;
   c62770  =   .25*_amt25pc;
   _tamt2  =  c62747 + c62755 + c62770;
   if FLPDYR eq 2013 then do;  
      if _ngamty gt _brk6{FLPDYR,MARS} then 
         _amt = .05*min(_alminc,c62740);
      else if _alminc gt _brk6{FLPDYR,MARS} then
         _amt = .05*min(_alminc-_brk6{FLPDYR,MARS},c62740);
      else 
         _amt = 0;
      _tamt2 = _tamt2 + _amt;
   end;
end;

if FLPDYR eq 2003 then do;
   c62746 = c24532 + x62746;
   c62748 = sum(e24583,0) + x62748;
   _line45  = min(_alminc,c62720,c24532);
   _line46 = c62746;
   _amt5pc  = max(0,min(_line46,_line45));
   c62747   = .05*_amt5pc;
   if _line45 gt 0 then do; 
      _line49  = max(0,_line45 - _amt5pc);
      _line50  = c62748;
      _amt8pc  = min(_line49,_line50);
      c62749   = .08*_amt8pc;
      _amt10pc = _line49 - _amt8pc;
      c62750   =  .1*_amt10pc;
   end;
   else if _line45 eq 0 then do;
     _amt8pc = 0;
     _amt10pc = 0;
     c62749 = 0;
     c62750 = 0; 
   end;
   _line55  = c62746 - _amt5pc;
   _line56  = min(c62720,_alminc) - _line45;
   _amt15pc = min(_line55,_line56);
   c62755   =  .15*_amt15pc;
   _amt20pc = _line56 - _amt15pc;
   c62760   =  .2*_amt20pc;
   if c62730 gt 0 then
      _amt25pc = min(_alminc,c62740) - min(_alminc,c62720);
   else
       _amt25pc = 0;
   c62770   =  .25*_amt25pc;
   _tamt2   = c62747 + c62749 + c62750 + c62755 + c62760 + c62770;
end;

c62800 = min(c62780,c62745+_tamt2-_amtfei);
c63000 = c62800 - c62900;;
c63100 = _taxbc-sum(e07300) - c05700;
if FLPDYR ge 2011 then c63100 = c63100 + e10105;

c63100 = max(0,c63100);
c63200 = max(0,c63000 - c63100);
*if _exact and f6251 eq 0 then c63200 = 0;
c09600 = c63200;
_othtax = sum(e05800)-sum(e05100,e09600,0);

if FLPDYR ge 2000 then
  c05800 = _taxbc  + c63200;
else
  c05800 = _taxbc;

/* form 2441 */

if _fixeic = 1 then _earned = e59560;
if MARS eq 2 then do;
  if _puf then do;    
     c32880 = .5*_earned;
     c32890 = .5*_earned;
  end;
  else do;
     c32880 = max(0,e32880);
     c32890 = max(0,e32890);
  end;
end;
else if MARS ne 2 then do;
  c32880 = _earned;
  c32890 = _earned; /*XX should this be zero? */
end;
 
_ncu13 = 0;
if _puf and f2441 ne . then
  _ncu13 = f2441;
else do;
  if CDOB1 gt 0 then _ncu13 = _ncu13+1;
  if CDOB2 gt 0 then _ncu13 = _ncu13+1;
end;
_dclim = min(_ncu13,2)*_dcmax{FLPDYR};
c32800 = min(max(e32800,e32750+e32775),_dclim);  
 
/* Part III of Dependent Care Benefits  XX what form number?*/

if _cmp then do;
   if MARS eq 2 then
     _seywage = min(c32880,c32890,min(e33420 + e33430 - e33450,e33460));
   else
     _seywage = min(c32880,min(e33420 + e33430 - e33450,e33460));
 
   c33465 = sum(e33465);
   c33470 = sum(e33470);
   c33475 = max(0,min(_seywage,5000/_sep) - c33470);
   c33480 = max(0,e33420 + e33430 - e33450 - c33465 - c33475);
   c32840 = c33470 + c33475;
   c32800 = min(max(0,_dclim - c32840),max(0,sum(e32750,e32775)- c32840));
end;

if MARS eq 2 then 
  c33000 = max(0,min(c32800, c32880,c32890));
else  
  c33000 = max(0,min(c32800,_earned));

/* Expenses limited to earned income  */

if _exact then do;
   _tratio = ceil(max((c00100 - _agcmax{FLPDYR})/2000,0)); 
   c33200 = c33000*.01*max(20,_pcmax{FLPDYR} - min(15,_tratio));
end;
else 
   c33200 = c33000*.01*max(20,_pcmax{FLPDYR}-max((c00100 - _agcmax{FLPDYR})/2000.,0.));
 
c33400 = min(max(0,c05800 - sum(e07300)), c33200);  /* Amount of the credit  */
if e07180 eq 0 then c07180 = 0; else c07180 = c33400;

/* Rate reduction credit for 2001 only */

if dsi eq 0 and c04800 gt 0 and FLPDYR eq 2001 and e07970 gt 0 then do;
  if MARS in(1,3,6) then 
     c07970 = min(300,c05800); 
  else if MARS eq 4 then 
     c07970 = min(500,c05800);
  else if MARS in(2,5) then 
     c07970 = min(600,c05800);
  else 
     do; put "Invalid MARS " MARS; stop;end;
end;
else
  c07970 = 0;
x07970 = c07970;

if _fixup ge 3 then c05800 = c05800 + _othtax;

if _exact then c59560 = x59560; else c59560 = _earned;

/* Number of dependents for EIC */
_ieic = 0;
if _puf and EIC ne . then
  _ieic = EIC;
else
  _ieic = (EICYB1>0) + (EICYB2>0) + (EICYB3>0);
/* Modified AGI only through 2002*/
_modagi = c00100 + e00400;
if FLPDYR lt 2003 then do;
 if e01000 lt 0 then _modagi = _modagi - e01000;
 if e02000 lt 0 then _modagi = _modagi - e02000;
 if e00900 lt 0 then _modagi = _modagi - .75*e00900;
end;

c59660 = 0;
if  MARS in (1,2,4,5,7) and _modagi gt 0 then do;
  if MARS eq 2 then
     _val_ymax = _ymax(_ieic,FLPDYR) + _joint{FLPDYR};
  else
     _val_ymax = _ymax(_ieic,FLPDYR);
  c59660 = min(_rtbase{_ieic,FLPDYR}*c59560,_crmax{_ieic,FLPDYR});
  _preeitc = c59660;
  if _modagi gt _val_ymax or c59560 gt _val_ymax then
  c59660 = max(0,c59660 - _rtless{_ieic,FLPDYR}*(max(_modagi,c59560)-_val_ymax));
  _val_rtbase = _rtbase{_ieic,FLPDYR}*100;
  _val_rtless = _rtless{_ieic,FLPDYR}*100;
/* disqualified income for EITC starts in 1997 */
  if FLPDYR ge 1997 then do;
/* Schedule E not included per suggestion of Pearce */
     _dy= e00400 + e83080 + e00300 + e00600 
     + max(0,max(0,e01000) - max(0,sum(e40223))) 
     + max(0,max(0,e25360)-e25430-e25470-e25400-e25500)
     + max(0,sum(e26210,e26340,e27200,-abs(sum(e26205)),-abs(e26320)));
    if _dy gt _dylim{FLPDYR} then c59660 = 0;
  end;
end;
if _cmp and _ieic eq 0 then do;
if (SOIYR- DOBYR ge 25 and SOIYR -  _DOBYR lt 65) and
   (SOIYR-SDOBYR ge 25 and SOIYR - _SDOBYR lt 65) then c59660 = 0;
end;
if ((_agep<25 or _agep ge 65) or (_ages lt 25 or _ages ge 65)) 
   and _agep ne . and _ages ne . and _ieic eq 0 then c59660 = 0;

/* Child tax credit */

c11070  = 0;
c07220  = 0;
c07230  = 0;
_precrd = 0;

_num = 1;
if MARS eq 2 then _num = 2;

if FLPDYR ge 1998 then do;
    _precrd = _chmax{FLPDYR}*_nctcr;
    if FLPDYR ne 2001 then
       _ctcagi = sum(c00100,_feided);
    else
      _ctcagi = c00100 + e34900 + e35200 + e35500;

    if _ctcagi gt _cphase(MARS) then do;
       if _exact then
          _precrd=max(0,_precrd-50*ceil(max(0,_ctcagi-_cphase(MARS))/1000));
       else
          _precrd=max(0,_precrd-50*(max(0,_ctcagi-_cphase(MARS))+500)/1000);

    end;


/* Hope Credit for 1998-2009 */
     c87520 = 0;
     if _puf then do;
        if FLPDYR in (1998,1999,2005:2009) then
           c87520 = e87520;
         else if FLPDYR in(2000:2004) then
           c87520 = e87500 + e87510;
     end;
     else do;
        if FLPDYR in(2002:2009) then do; 
           c87480 = max(0,min(e87480,2*_hopelm(FLPDYR)));
           c87485 = max(0,min(e87485,2*_hopelm(FLPDYR)));
           c87490 = max(0,min(e87490,2*_hopelm(FLPDYR)));
           c87495 = max(0,min(e87495,2*_hopelm(FLPDYR)));
      /*   

  c87481 = .5*(c87480 + min(c87480,_hopelm(FLPDYR)));
           c87486 = .5*(c87485 + min(c87485,_hopelm(FLPDYR)));
           c87491 = .5*(c87490 + min(c87490,_hopelm(FLPDYR)));
           c87496 = .5*(c87495 + min(c87495,_hopelm(FLPDYR)));
           c87520 = c87481 + c87486 + c87491 + c87496;
*/




  c87500 = min(c87480,_hopelm{FLPDYR})+min(c87485,_hopelm{FLPDYR})+min(c87490,_hopelm{FLPDYR})
                    +min(c87495,_hopelm{FLPDYR});
           c87510 = .5*(c87480+c87485+c87490+c87495-c87500);
           c87520 = c87500+c87510;





        end;
        else if FLPDYR in(1998:2001) then do; 
           c87500 = e87500;
           c87510 = e87510;
           c87520 = c87500 + c87510;
           end;     
     end;

/* American Opportunity Credit 2009+*/

       
       if _cmp and FLPDYR ge 2009 then do;
        c87482 = max(0,min(e87482,4000));
        c87487 = max(0,min(e87487,4000));
        c87492 = max(0,min(e87492,4000));
        c87497 = max(0,min(e87497,4000));
        if max(0,c87482-2000) eq 0 then c87483 = c87482; else c87483 = 2000+.25*max(0,c87482-2000); 
        if max(0,c87487-2000) eq 0 then c87488 = c87487; else c87488 = 2000+.25*max(0,c87487-2000);
        if max(0,c87492-2000) eq 0 then c87493 = c87492; else c87493 = 2000+.25*max(0,c87492-2000);
        if max(0,c87497-2000) eq 0 then c87498 = c87497; else c87498 = 2000+.25*max(0,c87497-2000);
        c87521 = c87483 + c87488 + c87493 + c87498;
       end;

/*Lifetime Learning Credit*/

    if _puf then
       if FLPDYR in(1998,1999) then do;
          c87540 = 0;
          c87550 = e87550;
          end;
       else if FLPDYR ge 2000 then do;
          c87540 = min(sum(e87530),_learn{FLPDYR})  ;
          c87550 = .2*c87540;
          end;
       else
          c87550 = 0;

    else do;
       if FLPDYR in(1998:2001) then  
          c87530 = e87530;
       else if FLPDYR ge 2002 then 
          c87530 = e87526 + e87522 + e87524 + e87528;

       c87540 = min(c87530,_learn{FLPDYR});
       c87550 = .2*c87540;
       if (_katrina gt 0 and flpdyr in(2008,2009)) or (e87542 gt 0 and flpdyr in(2005,2006)) then c87550 = .4*c87540;
    end;

/* Refundable American Opportunity Credit 2009+*/
    c87668 = 0;
    if _cmp and (FLPDYR ge 2009 and c87521 gt 0) then do;
      c87654 = 90000*_num;
      c87656 = c00100;
      c87658 = max(0,c87654 - c87656);
      c87660 = 10000*_num;
      c87662 = 1000*min(1,c87658/c87660);
      c87664 = c87662*c87521/1000.;
      if EDCRAGE eq 1 then c87666 = 0; else c87666= .4*c87664;
      c10960 = c87666;
      c87668 = c87664 - c87666;
      c87681 = c87666;
     end;


/* Nonrefundable Education Credits */


/* Form 8863 Tentative Education Credits*/
    if FLPDYR ge 1998 then c87560 = c87520 + c87550;
 
/*Phase out*/
    if MARS eq 2 then c87570 = _edphhm{FLPDYR}*1000;
    else c87570 = _edphhs{FLPDYR}*1000;
    c87580 = c00100;
    c87590 = max(0,c87570 - c87580);
    c87600 = 10000*_num;
    c87610 = min(1,c87590/c87600);
    c87620 = c87560 * c87610;
    if FLPDYR le 2008 then
       c07230 = c87620;
    else if FLPDYR eq 2009 then do;
       c87625 = c87620 + c87668;
       c07230 = c87625;
    end;
    else if FLPDYR eq 2010 or FLPDYR eq 2011 then do;
       _xlin4 = max(0,c05800 - (e07300 + c07180 + e07200));
       _xlin5 = min(c87620,_xlin4);
       _xlin8 = e07300 + c07180 + e07200 + _xlin5;
       _xlin9 = max(0,c05800 - (e07300 + c07180 + e07200 + _xlin5));
       _xlin10 = min(c87668,_xlin9);
       c87680 = _xlin5 + _xlin10;
       c07230 = c87680;
    end;
end;

_ctc1 = c07180 + e07200 + c07230;
_ctc2 = 0;
if FLPDYR ge 2009            then _ctc2 = e07240 + e07960 + e07260;
if FLPDYR in(2002:2005,2008) then _ctc2 = e07240;
if FLPDYR eq 2006            then _ctc2 = e07240 + e07260;
if FLPDYR eq 2001            then _ctc2 = c07970;
if FLPDYR ge 2000            then _ctc2 = _ctc2 + sum(e07300);
_regcrd = _ctc1 + _ctc2;
_exocrd = e07700 + e07250;
if FLPDYR ge 1997 then _exocrd = _exocrd + t07950;
_ctctax = c05800 - _regcrd -_exocrd;
c07220 = min(_precrd,max(0,_ctctax));    /* lt tax owed */

/* Additional Child Tax Credit */

c82940 =0;
if (FLPDYR in(1998:2000) and _nctcr gt 2) or
   (FLPDYR ge 2001 and _nctcr gt 0) then do;
/* Part I  of 2005 form 8812 */
    c82925 = _precrd;
    c82930 = c07220;
    c82935 = c82925 - c82930; /* CTC not applied to tax  */
    c82880  = max(0,e00200+e82882+e30100+max(0,_sey)-.5*_setax);
    if _exact then c82880 = e82880;
    h82880 = c82880;
    c82885 = max(0 ,c82880 - _ealim{FLPDYR});
    c82890 = _adctcrt(FLPDYR)*c82885;
/* Part II  of 2005 form 8812 */
    if FLPDYR ge 2001 and _nctcr gt 2 and c82890 lt c82935 then do;
       c82900 = .0765*min(_ssmax{FLPDYR},c82880);
        *c82900 = e82900;
       c82905 = e03260 + e09800;
       c82910 = c82900 + c82905;
       c82915 = c59660 + e11200;
       c82920 = max(0,c82910-c82915);
       c82937 = max(c82890,c82920);
    end;

/* Part III  of 2005 form 8812 */

    if FLPDYR ge 2001  then do;
       if _nctcr le 2 and c82890 gt 0 then c82940 = min(c82890,c82935);
       if _nctcr gt 2 then do;
          if c82890 ge c82935 then 
             c82940 = c82935;
          else 
             c82940 = min(c82935,c82937);

       end;
    end;
    else do; 
      c82900 = .0765*min(_ssmax{FLPDYR},c82880);
      c82905 = e03260 + e09800 + e09200;
      c82910 = c82900 + c82905;
      c82915 = c59660 + e11200;
      c82920 = max(0,c82910 - c82915);
      c82940 = min(c82920,c82935);
    end; 
  c11070 = c82940;

  if _puf then e59660 = e59680 + e59700 + e59720;
  _othadd = e11070 - c11070;
  if _fixup ge 4 then c11070 = c11070 + _othadd;
  
  if c11070 eq 0 then do over _a8812; _a8812 = 0;end;
end;

/* Form 5405 First-Time Homebyuyer credit*/

c64450 = 0;
if FLPDYR ge 2008 and FLPDYR le 2010 then do;
   if FLPDYR eq 2008 then c64445 = min(7500/_sep,e64445);
   if FLPDYR ge 2009 then c64445 = min(8000/_sep,e64445);
   c64446 = c00100;
   if FLPDYR eq 2008 then _phbuy = 150000/_sep;
   if FLPDYR eq 2010 then do;
      _phbuy = 125000;
      if MARS eq 2 then _phbuy = 225000;
   end;
   if (c64446  gt _phbuy and FLPDYR ne 2009) or
      (e64447 gt 0 and FLPDYR eq 2009) then do;
      if FLPDYR ne 2009 then c64447 = c64446 - _phbuy;
      if FLPDYR eq 2009 then c64447 = e64447;
      c64448 = min(1,c64447/20000);
      c64449 = c64445*c64448;
      c64450 = c64445 - c64449;
   end;
   else c64450 = c64445;
end;

/* Credits 1040 line 48 */

c07100 = e07180 + e07200 + c07220 + c07230 + e07250 
       + e07600 + e07260 + c07970 + e07300 + x07400 
       + e07500 + e07700 + e08000;
y07100 = c07100; 

if FLPDYR ge 2002 then c07100 = c07100 + e07240;
if FLPDYR ge 2007 then c07100 = c07100 + e08001;
if FLPDYR ge 2009 then c07100 = c07100 + e07960 + e07970;
if FLPDYR in(2002:2004) and SOIYR in(2002:2004) then C07100 = c07100 + e07980;
if FLPDYR GE 2009       and SOIYR GE 2009       then c07100 = c07100 + e07980;
if FLPDYR in(2007:2008) then c07100 = c07100 + e07910;
if FLPDYR in(2007,2009) then c07100 = c07100 + e07920 + e07930;
  
if FLPDYR ge 1994 and FLPDYR le 2007 then c07100 = c07100 + e07900;
x07100 = c07100;
c07100 = min(c07100,c05800);

/* Tax after credits  1040 line 52 */
_eitc = c59660;
*c08800 = max(0,c05800 - _eitc);
c08795 = max(0,c05800 - c07100);

c08800 = c08795;
if _puf then e08795 = e08800;

/*if _fixup ge 3 then
   c08800 = max(0,c08800 + _othtax);
else
   c08800 = max(0,c08800);
*/

/*tax before refundable Credits*/

c09200 = c08795 + e09900 + e09400 + e09800 + e10000 + e10100;
if FLPDYR lt 2000 then c09200 = c09200 + c09600;
if FLPDYR ge 1994 then c09200 = c09200 + sum(0,e09700);
if FLPDYR ge 1995 then c09200 = c09200 + e10050;
if FLPDYR ge 1996 then c09200 = c09200 + e10075;
if FLPDYR ge 2007 then c09200 = c09200 + e09805;
if FLPDYR ge 2010 then c09200 = c09200 + e09710 + e09720;

/* Decomposition of EITC */
if c08795 gt 0 and c59660 gt 0 then do;
  if c08795 le c59660 then do;
     c59680 = c08795;
     _comb = c59660 - c59680;
     end;
  else do;
     c59680 = c59660; 
     _comb = 0;
     end;
  if _comb gt 0 and c09200 - c08795 gt 0 then
     if c09200 - c08795 gt _comb then c59700 = _comb;
     else do; 
        c59700 = c09200 - c08795;
        c59720 = c59660 - c59680 - c59700;
     end;
end;
else if c08795 eq 0 and c59660 gt 0 then do; 
     c59680 = 0;
     if c09200 gt 0 then 
        if c09200 gt c59660 then 
	    c59700 = c59660;
	else do; 
	    c59700 = c09200;
            c59720 = c59660 - c59700;
        end;
      else
         c59720 = c59660;
end;
else do;
  _compb = 0;
  c59680 = 0;
  c59700 = 0;
  c59720 = 0;
end;
c07150 = c07100 + c59680;
if FLPDYR ge 2008 then c07150 = c07150;

if FLPDYR in(2009,2010) and c00100 lt 95000*_txp and e00200 gt 0 then do;
  c87845 = min(.062*_earned,400*_txp);
  c87865 = .02*max(0,c00100 + _feided - 75000*_txp);
  c87870 = max(0,c87845-c87865);
  c87875 = e87875;
  if FLPDYR eq 2009 then do;
    c87880=e87880;
    c87885 = c87875+c87880;
    c87890 = max(0,c87870-c87885);
    c87895=c87880+c87890;
    end; 
  else if FLPDYR eq 2010 then 
    c87895 = max(0,e87870-e87875);
 
  c10950=c87895;
  end;
else
  c10950 = 0;

/*SOI Tax (Tax after non-refunded credits plus tip penalty */

c10300 = c09200 - e10000 - e59680 - e59700;
if FLPDYR ge 1998 then c10300 = c10300 - e11070;
if FLPDYR in(2008:2010) then c10300 = c10300 - sum(0,e11570); /* e11570 sometimes missing */
if FLPDYR ge 2007 then c10300 = c10300 - e11550;
if FLPDYR eq 2008 then c10300 = c10300 - sum(0,e11580);
if FLPDYR ge 2009 then c10300 = c10300 - e09710 - e09720 - e11581 - e11582;
if FLPDYR ge 2009 then c10300 = c10300 - e87900 - e87905 - e87681 - e87682;
if FLPDYR ge 2010 then c10300 = c10300 - c10950 - e11451 - e11452;
if FLPDYR ge 2011 then c10300 = c09200 - e09710 - e09720 - e10000 - e11601 - e11602;
if FLPDYR eq 2010 then c10300 = c10300 + c10950;
c10300 = max(c10300,0);

/* Ignore refundable part of _eitc to obtain SOI Income Tax */
if c09200 le _eitc and _eitc ne . then do;
   _eitc = c09200 ;
   c10300 = 0;
end; *eNd;


%MEND COMP;
%MACRO STATAX(IN,OUT);
/* To use this macro the "taxsim9" binary must be in the executable path.
   The "IN" argument is a SAS format datafile with the SOI E-codes.
   The "OUT" argument is a new SAS format datafile with all of the "IN"
   variables, and 41 additional variables. The new variables are documented
   at http://www.nber.org/taxsim/taxsim-calc9.html
*/
data _taxpayer;
set &IN;
array _x _x01 _x02 _x03 _x04 _x05 _x06 _x07 _x08 _x09 _x10 _x11
         _x12 _x13 _x14 _x15 _x16 _x17 _x18 _x19 _x20 _x21 _x22;
_posagi = max(0.0d0,E00100);
_x01 = _n_;retain _aged (
_x02 = FLPDYR;

if STATE ne . then _x03 = STATE; else _x03 = 0;

array _mars24{1:5} _temporary_;
retain _mars24 (1 2 6 3 5);
_x04 = _mars24{MARS};
if DSI gt 0 then _x04 = 8;
_x05 = sum(XOCAH, XOCAWH, XOODEP, XOPAR);

array age(12,1996:2013) _temporary_;
/*
1996   1997   1998   1999   2000   2001   2002   2003   2004   2005   2006   2007   2008   2009   2010   2011  2012  2013
*/
retain age (
5000   5150   5300   5350   5500   5650   5850   5900   6050   6250   6400   6650   6800   7100   7100   7200  7400  7400
6000   6150   6350   6400   6600   6750   7000   7050   7250   7500   7650   7950   8150   8500   8500   8600  8850  8850
7500   7700   7950   8050   8200   8500   8750  10450  10650  11000  11300  11750  11950  12500  12500  12700 12950 11000
8300   8500   8800   8900   9050   9400   9650  11400  11600  12000  12300  12800  13000  13600  13600  13800 14000 12050 
9100   9300   9650   9750   9900  10300  10550  12350  12550  13000  13300  13850  14050  14700  14700  14900 15050 13100
9900  10100  10500  10600  10750  11200  11450  13300  13500  14000  14300  14900  15100  15800  15800  16000 16100 14150  
4150   4250   4400   4450   4525   4700   4825   5700   5800   6000   6150   6400   7000   6800   6800   6900  7000  6025
4950   5050   5250   5300   5375   5600   5725   6650   6750   7000   7150   7450   8050   7900   7900   8000  8050  7075
5750   5850   6100   6150   6225   6500   6625   7600   7700   8000   8150   8500   9100   9000   9000   9100  9100  8125
6550   6650   6950   7000   7075   7400   7525   8550   8650   9000   9150   9550  10150  10100  10100  10200 10150  9175
6900   7050   7300   7300   7400   7750   8050   8150   8350   8550   8800   9150   9350   9750   9800   9900  9950 10200 
7900   8050   8350   8450   8650   8850   9200   9300   9550   9800  10050  10450  10700  11150  11200  11300 11400 11650 );





array _d9src(12) _temporary_;
retain _d9src ( 1 1 1 2 2 2 1 2 2 2 1 1);

/*    Age Exemptions */;
_x06 = 0;
if year ge 1962 and year le 1978 then
   _x06=agex;
else if year ge 1982 and year le 1995 then do;
   if agex eq 0 then _x06 = 0;
   if agex eq 1 or agex eq 2 then _x06 = 1;
   if agex eq 3 then _x06 = 2;
end;
else if year ge 1996 and fded eq 2 then
   do i = 1 to 12 ;
      if age(i,year) eq _totald then _x06    = _d9src(i);
   end;
_x06 = min(_x06,2);
_x07   = E00200 + E00900;
_x07   = sum(E00200,E00900);
_x08   = 0;
if year le 2002 then _x09   = E00600; else _x09   = E00650;
_x10   = sum(E02000,E01400,E00300,E00700,E00800,
             E01200,E02100,E02600,E01100,E02800)
        -sum(E02540,E02700,E03150,E03260,E03270,E03300,E03500,
             E03400,E03280,E03290,E03230,E03210,E03700);
_x11   = E01700;
_x12   = E02400;
_x13   = E00400;
_x14   = 0; /* rent paid*/
_x15   = E18500;
_x16   = max(0,E20400-.02*_posagi);
_x17   = E32800;
_x18   = E02300;
if  N24 ne . then _x19 = N24; else _x19 = XOCAH;
_x19 = min(_x19,_x05);
_x20   = sum(E19200,max(0,E17500-.075*_posagi),E19700,max(0,E20500-.1*_posagi));
_x21   = E22250;
_x22   = E23250;

file "/tmp/txpydata.raw";
if _n_ eq 1 then put "9 85 2 /";
put      _x01 _x02 _x03 _x04 _x05 _x06 _x07 _x08 _x09 _x10 _x11
         _x12 _x13 _x14 _x15 _x16 _x17 _x18 _x19 _x20 _x21 _x22;
run;

x  "unset noclobber;./taxsim9 </tmp/txpydata.raw   >/tmp/results.raw;" xwait;
%PUT 'taxsim9 return code: ' &SYSRC;

data _taxsim;
infile "/tmp/results.raw" lrecl=2048;
input _x01 year state fiitax siitax fica frate srate ficar v10-v41;
run;

data &OUT;
merge _taxpayer _taxsim;
by _x01;
run;
%MEND STATAX;

/*Schedule D */
%MACRO SCHD;

       c22256        c22556 c23650 c23656 c24505 c24510 c24516
c24517 c24520 c24530 c24532 c24533 c24534 c24535 c24540 c24550 c24560 
c24567 c24570 c24580 c24581 c24585 c24587 c24590 c24595 c24597 c24598 
c24600 c24605 c24610 c24615 c59430        c59450 c59460 c59475 c59480
c59485 c59490

%MEND;

/*Form 4972 */
%MACRO
F4972; c59430        c59450 c59460 c59475 c59480 c59485 c59490
%MEND;

/* Form 8812 */
%MACRO F8812;

c82880 c82885 c82890 c82900 c82905 c82910 c82915 c82920 c82925 c82930 
c82935 c82937 c82940

%MEND;


/*
   EVALUES is a complete list of all variables used by the tax calculator,
*/

%MACRO EVALUES;

e00100   e00200 e00250 e00300 e00400   e00600   e00650   e00700 e00800 e00900 
e01000   e01100 e01150 e01200 e01400   e01700   e02000   e02100 e02300 e02400   
e02500   e02540 e02600 e02605 e02610   e02615   e02700   e02800 e03150 e03200   
e03210   e03220 e03230 e03240 e03260   e03270   e03280   e03290 e03300 e03400   
e03500   e03600 e03700 e03900 e04000   e04100   e04200   e04250 e04470 e04500   
e04600   e04800 e04805 e05100 e05200   e05700   e05800   e07180 e07200 e07220   
e07230   e07240 e07250 e07260 e07300   e07400   e07500   e07600 e07700 
e07900   e07910 e07920 e07930 e07960   e07970   e07980   e08000 e08001 t08795 
e08795   e08800 e09200 e09400 e09600   e09700   e09710   e09720 e09800 e09805 
e09900   e10000 e10050 e10075 e10100   e10105   e11055   e11070 e11200 e11451 
e11452   e11550 e11580 e11581 e11582   e11601   e11602   e15360 e17500  
t18300   e18300 e18400 e18425 e18450   e18500   e18600   t18600 e18800 e18900 
e19200   e19400 e19500 e19530 e19550   e19570   e19575   e19700 e19800 e19850 
e20100   e20200 e20300 e20400 e20500   e20550   e20600   e20800 e20900 e20950 
e21000   e21010 e21040 e21606 e21626   e21776   e22250   e22256 e22306 e22326 
e22366   e22376 e22550 e22556 e23250   e23650   e23656   e23660 e24510 
e24515   e24516 e24517 e24518 e24520   e24530   e24532   e24533 e24534 
e24535   e24550 e24560 e24570 e24580   e24581   e24583   e24585 e24587 e24590 
e24595   e24597 e24598 e24600 e24605   e24610   e24615   e25350 e25360 e25400 
e25430   e25470 e25500 e26205 e26210   e26320   e26340   e27200 e30100 e32750 
e32775   e32800 e32880 e32890 e33420   e33430   e33450   e33460 e33465 e33470 
t34900   e34900 e35200 e35500 e35600   t35800   e35800   e35905 e35910 e35910_0 
e37717   e40223 e58980 e58990 e59280   e59400   e59410   e59420 e59440 e59470 
e59490   e59560 e59660 e59680 e59700   e59720   e60000   e60100 e60130 e60200 
e60220   e60240 e60250 e60260 e60290   e60300   e60340   e60405 e60410 e60420 
e60430   e60440 e60460 e60480 e60500   e60550   e60600   e60620 e60630 e60640 
e60660   e60680 e60720 e60820 e60840   e60860   e60900   e61400 e61450 e61850 
e62000   e62100 e62600 e62720 e62730   e62740   e62746   e62748 e62900 e87482 
e87287   e87292 e87297 e64445 e64447   e74400   e82880   e82882 e82900 e83080 
e83200_0 e84200 e84220 e87480 e87485   e87490   e87487   e87492 e87497 e87495 
e87500   e87510 e87520 e87522 e87524   e87526   e87528   e87530 e87542 e87550 
e87654   e87656 e87660 e87664 e87666   e87900   e87905   e87681 e87682 e87875 
e87870   e87880 e99998 e99999 e35300   e35300_0 e35600_0 e63200 e07100 t07400 
e11583   e10300 e01300 e11570

%MEND EVALUES;

%MACRO MISC;

xocah   xocawh   flpdyr    soiyr     agep      ages      mars      eic       n11 
N24     xtxcr1-xtxcr10     pbi       sbi       xtot      dsi       s006      weight 
flpdmo  xoodep   t27800    f4972     dobyr     eicyb1    eicyb2    eicyb3    cdob1 
cdob2   fded     sdobyr    ssind     schj      schjin    f8814     f2441     DOBMD 
midr    sdobmd   f2555     t04470    t35200    t35910    t35911    t07950    t35905 
t35500  RECID TXST F6251 SCHA F8914 SCHM SCHD edcrage

%MEND MISC;

%MACRO CVALUES;
/*
  CVALUES is a complete list of values calculated by the tax calculator.
*/

c00100 c00650 c01000 c01100 c02500 c02650 c02900 c04100 c04200 c04250 
c04470 c04500 c04600 c04800 c04805 c05100 c05200 c05700 c05750 c05800 
c06300 c07100 c07150 c07180 c07220 c07230 c07970 c08795 c08800 c09200 
c09600 c10300 c11055 c11070 c11580 c15100 c15200 c15250 c17000 c17750 
c18300 c19200 c19570 c19700 c20400 c20500 c20750 c20800 c21040 c21040 
c21060 c22250 c22256 c22556 c23250 c23650 c23656 c24505 c24510 c24515 
c24516 c24516 c24517 c24520 c24530 c24532 c24533 c24534 c24535 c24540 
c24540 c24550 c24560 c24560 c24567 c24570 c24580 c24581 c24585 c24587 
c24590 c24595 c24597 c24598 c24600 c24600 c24605 c24610 c24615 c63100 
c32800 c32840 c32880 c32890 c33000 c33200 c33400 c33420 c33430 c33450 
c33460 c33465 c33470 c33475 c33480 c37703 c59430 c59450 c59460 c59475 
c59480 c59485 c59490 c59560 c59660 c59680 c59700 c59720 c60000 c60000 
c60130 c60200 c60220 c60240 c60260 c62100 c62600 c62700 c62720 c62730 
c62740 c62745 c62746 c62747 c62748 c62749 c62750 c62755 c62760 c62770 
c62780 c62800 c62900 c63000 c63100 c63200 c64445 c64446 c64446 c64447 
c64448 c64449 c64450 c82880 c82880 c82885 c82890 c82900 c82905 c82910 
c82915 c82920 c82925 c82930 c82935 c82937 c82940 c87480 c87485 c87490 
c87495 c87500 c87510 c87520 c87530 c87540 c87550 c87560 c87570 c87580 
c87590 c87600 c99998 c99999

%MEND CVALUES;

%MACRO CVARS;

00100 00650 01000 02500 02650 02700 02900 03290 04100 04200 04470 04500 04600 
04800 04805 05100 05200 05700 05750 05800 07100 07180 07220 07970 08795 08800 
09200 09600 10300 11070 17000 17750 18300 19200 19570 19700 20400 20500 20750 
20800 21040 21060 32800 32880 32890 33000 33200 33400 59560 59660 62100 62600 
62700 62745 62747 62749 62750 62755 62760 62770 63000 63200 37703 58974 59700 
59720 59680 99998 99999

%MEND CVARS;


%MACRO WVALUES;

e00100 e00200 e00400 e00600 e00650 e01700 e02000 e02300 e02400 e03150 e03300
e17500 e18500 e19200 e19700 e20400 e20500 e22250 e23250 e32800 year agex fded 
xocah xocawh xopar mars flpdyr state N24 

%MEND;


%MACRO NBERVARS;

_puf _sep _totald _ymod _ieic _agi _agierr _prexmp _posagi _dispc 
_ratio _tratio  _sit _statax _smpl _dedmin _dedpho _numextra 
_txpyers _standard _othded _noncg  _taxltg _taxspecial _dwks16 _dwks26 
_dwks29 _dwks27 _dwks22 _dwks12 _dwks17 _dwks13 _dwks8 _dwks6 _dwks5 _dwks9 
_dwks29 _dwks21 _dwks25 _dwks26 _dwks28 _dwks31 _dwks34 _dwks39 _dwks40 
_dwks42 _dwks45 _addamt _edical _cmbtp _totadp _ngamty _amt5pc _amt15pc 
_amt25pc _tamt2 _line49 _line50 _amt8pc _amt10pc _line55 _line56 _amt20pc 
_taxbc _othtax _sey _earned _setax _fica _modagi _dy _val_rtless
_val_crmax _val_ymax _nctcr _precrd _ctctax _othadd _comb _eitc _val_rtbase
_line22 _line23 _line25 _line26 _line28 _line49 _line50 _iyr _ncu13 _dclim
_seywage _preeitc _txp _phase2 _rltaxsd _txpyers _phbuy _hmbcrd1 _hmbcrd2
_taxinc _alminc _alminy _amtfei _feided _feitax _ctcagi _dispx _dispc
_fixeic _fixup _nearn _agep _ages _unpref1 unpref2 _oded _xyztax _katrina
_statax _parents _ymod1 _ymod2 _ymod3

%MEND NBERVARS;

%MACRO PUFVARS;

AGIR1  DSI    EFI    EIC    ELECT  FDED   FLPDYR FLPDMO F2441  F3800
F6251  F8582  F8606  IE     MARS   MIdR   N20    N24    N25    PREP
SCHB   SCHCF  SCHE   STATE  TFORM  TXST   XFPT   XFST   XOCAH  XOCAWH
XOODEP XOPAR  XTOT
E00200 E00300 E00400 E00600 E00650 E00700 E00800 E00900 E01000 E01100
E01200 E01400 E01500 E01700 E02000 E02100 E02300 E02400 E02500 E03150
E03210 E03220 E03230 E03260 E03270 E03240 E03290 E03300 E03400 E03500
E00100 E04470 E04250 E04600 E04800 E05100 E05200 E05800 E06000 E06200
E06300 E09600 E07180 E07200 E07220 E07230 E07240 E07260 E07300 E07400
E07600 E08000 E07150 E06500 E08800 E09400 E09700 E09800 E09900 E10300
E10700 E10900 E59560 E59680 E59700 E59720 E11550 E11070 E11100 E11200
E11300 E11400 E11570 E11580 E11581 E11582 E11583 E10605 E11900 E12000
E12200 E17500 E18425 E18450 E18500 E19200 E19550 E19800 E20100 E19700
E20550 E20600 E20400 E20800 E20500 E21040 E22250 E22320 E22370 E23250
E24515 E24516 E24518 E24535 E24560 E24598 E24615 E24570 E25350 E25370
E25380 E25470 E25700 E25820 E25850 E25860 E25940 E25980 E25920 E25960
E26110 E26170 E26190 E26160 E26180 E26270 E26100 E26390 E26400 E27200
E30400 E30500 E32800 E33000 E53240 E53280 E53410 E53300 E53317 E53458
E58950 E58990 E60100 E61850 E60000 E62100 E62900 E62720 E62730 E62740
E65300 E65400 E68000 E82200 T27800 S27860        E87500 E87510 E87520
E87530 E87540 E87550 RECID  S006   S008   S009   WSAMP  TXRT
weight soiyr 

/* added for tail.sas */
recno recida recid
%MEND;

%MACRO PUFX;
/* not in puf added for c00100*/
e01400 e02540 e02600 e02610 e02700 e20900 e21000 skip e03900 e03280 e03700
e02540 e02700
/* added for c04470 */
e18800 e18900 e21010 e21020

/* added for c05800 */
e62600

%MEND;

%MACRO INIT;
array _a8812 %F8812;
array _c %CVALUES;
array _e %EVALUES;
array _n %NBERVARS;
array _m %MISC;
array _a %EVALUES %CVALUES %NBERVARS %MISC;

/*Parameters of the tax law */

array _aged{2,1993:2013}     _temporary_;* extra std ded for aged;
array _amtage{1993:2013}     _temporary_;* Age for full AMT exclusion;
array _agcmax{1993:2013}     _temporary_;* ;   
array _almsp{1993:2013}      _temporary_;* AMT bracket;
array _adctcrt(1998:2013)    _temporary_;* Rate for additional ctc;
array _almsep{1993:2013}     _temporary_;* extra alminc for married sep;
array _almdep{1993:2013}     _temporary_;* Child AMT exclusion base;
array _amex {1993:2013}      _temporary_;* Personal Exemption;
array _amtex{1993:2013,6}    _temporary_;* AMT Exclusion;
array _amtsep{1993:2013}     _temporary_;* Additional alminc for joint;
array _amtys{6}              _temporary_;* AMT phaseout start;
array _brk1{1993:2013,6}     _temporary_;* 10% tax rate thresholds;
array _brk2{1993:2013,6}     _temporary_;* 15% tax rate thresholds;
array _brk3{1993:2013,6}     _temporary_;* 25% rate thresholds;
array _brk4{1993:2013,6}     _temporary_;* 28% rate thresholds;
array _brk5{1993:2013,6}     _temporary_;* 33% rate thresholds;
array _brk6{1993:2013,6}     _temporary_;* 35% rate thresholds;
array _chmax{1993:2013}      _temporary_;* Max Child Tax Credit per child;
array _cgrate1(1997:2013)    _temporary_;* Initial rate on long term gains;
array _cgrate2(1997:2013)    _temporary_;* Normal rate on long term gains;
array _crmax{0:3,1993:2013}  _temporary_;* max earned income credit;
array _cphase{6}             _temporary_;* Child Tax Credit Phase-Out;
array _dcmax(1993:2013)      _temporary_;* Max dependent care expenses;
array _dylim{1993:2013}      _temporary_;* Limits for Disqualified Income;
array _ealim{1993:2013}      _temporary_;* Max earn ACTC;
array _edphhs{1993:2013}     _temporary_;* end of educ phaseout - singles;
array _edphhm{1993:2013}     _temporary_;* end of educ Phaseout - married;
array _exmpb{1993:2013,6}    _temporary_;* Personal Exemption Amount;
array  _feimax(1993:2013)    _temporary_;* Maximum foreign earned income exclusion;
array _hopelm{1998:2009}     _temporary_;* limit for education expenses Hope credit;
array _joint{1993:2013}      _temporary_;* extra to ymax for joint;
array _learn{1993:2013}      _temporary_;* expense limit for the LLC;
array _pcmax{1993:2013}      _temporary_;* Maximum Percentage for f2441;
array _phase{1993:2013}      _temporary_;* Phase out for Itemized deds;
array _rt1{1993:2013}        _temporary_;* 10% rate;
array _rt2{1993:2013}        _temporary_;* 15% rate;
array _rt3{1993:2013}        _temporary_;* 25% rate;
array _rt4{1993:2013}        _temporary_;* 28% rate;
array _rt5{1993:2013}        _temporary_;* 33% rate;
array _rt6{1993:2013}        _temporary_;* 35% rate;
array _rt7{1993:2013}        _temporary_;* 39.6% rate;
array _rtbase{0:3,1993:2013} _temporary_;* EIC base rate;
array _rtless{0:3,1993:2013} _temporary_;* EIC _phaseout rate;
array _ssb50{6}              _temporary_;* SS 50% taxability threshold;
array _ssb85{6}              _temporary_;* SS 85% taxability threshold;
array _ssmax(1993:2013)      _temporary_;* SS Maximum taxable earnings;
array _stded{1993:2013,7}    _temporary_;* Standard Deduction;
array _thresx{6}             _temporary_;* threshold for add medicare tax;
array _ymax{0:3,1993:2013}   _temporary_;* start of EIC _phaseout;


/*              1993   1994   1995   1996   1997   1998   1999   2000   
  2001   2002   2003   2004   2005   2006   2007   2008   2009   2010   
  2011   2012   2013*/
                
retain _adctcrt(                                    .10    .10    .10
   .10    .10    .10    .15    .15    .15    .15    .15    .15    .15 
   .15    .15    .15);

retain _aged (   900    950    950   1000   1000   1050   1050   1100   
  1100   1150   1150   1200   1250   1250   1300   1350   1400   1400   
  1450   1450   1500
                 700    750    750    800    800    850    850    850    
   900    900    950    950   1000   1000   1050   1050   1100   1100   
  1150   1150   1200);

retain _almdep(    .      .      .      .      .   5000   5100   5200   
  5350   5500   5650   5750   5850   6050   6300   6400   6700   6700   
  6800   6950   6950);

retain _almsp(175000 175000 175000 175000 175000 175000 175000 175000 
175000 175000 175000 175000 175000 175000 175000 175000 175000 175000 
175000 175000 179500);

retain _amex (  2350   2450   2500   2550   2650   2700   2750   2800   
  2900   3000   3050   3100   3200   3300   3400   3500   3650   3650   
  3700   3800   3900);

retain _amtage(    0      0      0      0      0     15     15     15  
    15     15     15     15     19     19     19     19     24     24     
    24     24     24); 

retain _amtsep(165e3 165000 165000 165000 165000 165000 165000 165000 
173000 173000 191000 191000 191000 200100 207500 214900 216900 219900 
223900 232500 232500);

retain _almsep(22500  22500  22500  22500  22500  22500  22500  22500  
 24500  24500  29000  29000  29000  31275  33125  34975  35475  36225  
 37225  39375  39375);

retain _agcmax(10000  10000  10000  10000  10000  10000  10000  10000  
 10000  10000  15000  15000  15000  15000  15000  15000  15000  15000  
 15000  15000  15000);

retain _cgrate1(                              .1     .1     .1     .1     
    .1     .1    .05    .05    .05    .05    .05      0      0      0      
     0      0    .10);

retain _cgrate2(                              .2     .2     .2     .2    
    .2     .2    .15    .15    .15    .15    .15    .15    .15    .15    
   .15    .15    .20);

retain _chmax (    0      0      0      0      0    400    500    500    
   600    600   1000   1000   1000   1000   1000   1000   1000   1000   
  1000   1000   1000);

retain _crmax(     0    306    314    323    332    341    347    353    
   364    376    382    390    399    412    428    438    457    457    
   464    475    487 
                1434   2038   2094   2152   2210   2271   2312   2353   
  2428   2506   2547   2604   2662   2747   2853   2917   3043   3050   
  3094   3169   3250 
                1511   2528   3110   3556   3656   3756   3816   3888   
  4008   4140   4204   4300   4400   4536   4716   4824   5028   5036   
  5112   5236   5372
                1511   2528   3110   3556   3656   3756   3816   3888   
  4008   4140   4204   4300   4400   4536   4716   4824   5657   5666   
  5751   5891   6044);

retain _dcmax(  2400   2400   2400   2400   2400   2400   2400   2400   
  2400   2400   3000   3000   3000   3000   3000   3000   3000   3000   
  3000   3000   3000);

retain _dylim (    0      0      0      0   2250   2300   2350   2400   
  2450   2550   2600   2650   2700   2800   2900   2950   3100   3100   
  3150   3200   3300);

retain _ealim(     0      0      0      0      0      0      0      0  
 10000  10350  10500  10750  11000  11300  11750   8500   3000   3000   
 3000   3000   3000);

retain _edphhs(    0      0      0      0      0     50     50     50     
    50     51     51     52     53     55     57     58     60     60     
   61     62     63);

retain _edphhm(    0      0      0      0      0    100    100    100    
   100    102    103    105    107    110    114    116    120    120    
   122    124    126);

retain _feimax(70000  70000  70000  70000  70000  72000  74000  76000  
 78000  80000  80000  80000  80000  82400  85700  87600  91400  91500 
 92900  95100  97600);

retain _hopelm (                                   1000   1000   1000 
  1000   1000   1000   1000   1000   1100   1100   1200   1200);

retain _joint (    0      0      0      0      0      0      0      0      
     0   1000   1000   1000   2000   2000   2000   3000   5000   5000   
     5000   5000      0);

retain _learn (    0      0      0      0      0   5000   5000   5000   
  5000   5000  10000  10000  10000  10000  10000  10000  10000  10000  
 10000  10000  10000);

retain _pcmax(    30     30     30     30     30     30     30     30     
    30     30     35     35     35     35     35     35     35     35     
    35     35     35);

retain _phase(108450 111800 114700 117950 121200 124500 126600 128950 
132950 137300 139500 142700 145950 150500 156400 159950 166800 166800 
169550 169550 172250);

retain _rtbase(    0  .0765  .0765  .0765  .0765  .0765  .0765  .0765 
 .0765  .0765  .0765  .0765  .0765  .0765  .0765  .0765  .0765  .0765  
 .0765  .0765  .0765
               .1850  .2600  .3400  .3400  .3400  .3400  .3400  .3400 
 .3400  .3400  .3400  .3400  .3400  .3400  .3400  .3400  .3400  .3400 
 .3400  .3400  .3400
               .1840  .1950  .3000  .3600  .4000  .4000  .4000  .4000 
 .4000  .4000  .4000  .4000  .4000  .4000  .4000  .4000  .4000  .4000  
 .4000  .4000  .4000
               .1840  .1950  .3000  .3600  .4000  .4000  .4000  .4000 
 .4000  .4000  .4000  .4000  .4000  .4000  .4000  .4000  .4500  .4500 
 .4500  .4500  .4000);

retain _rtless(    0  .0765  .0765  .0765  .0765  .0765  .0765  .0765  
 .0765  .0765  .0765  .0765  .0765  .0765   .0765 .0765  .0765  .0765 
 .0765  .0765  .0765
               .1321  .1598  .1598  .1598  .1598  .1598  .1598  .1598 
 .1598  .1598  .1598  .1598  .1598  .1598   .1598 .1598  .1598  .1598  
 .1598  .1598  .1598
       	       .1393  .1768  .2022  .2106  .2106  .2106  .2106  .2106  
.2106  .2106   .2106  .2106  .2106  .2106   .2106  .2106  .2106  .2106  
.2106  .2106   .2106
               .1393  .1768  .2022  .2106  .2106  .2106  .2106  .2106  
.2106  .2106   .2106  .2106  .2106  .2106   .2106 .2106  .2106  .2106  
.2106  .2106   .2106);

retain _ssmax( 57600  60600  61200  62700  65400  68400  72600  76200  
 80400  84900  87000  87900  90000  94200  97500 102000 106800 106800 
106800 110100 115800);

retain _ymax(      0   5000   5150   5300   5450   5600   5700   5800   
  5950   6050   6240   6390   6550   6740   7000   7160   7470   7480   
 7590   7750    7970
               12200  11000  11300  11650  11950  12300  12500  12700  
 13090  13520  13730  14040  14400  14810  15390  15740  16420  16460  
 16690  17100  17530
               12200  11000  11300  11650  11950  12300  12500  12700  
 13090  13520  13730  14040  14400  14810  15390  15740  16420  16460  
 16690  17100  17530
               12200  11000  11300  11650  11950  12300  12500  12700  
 13090  13520  13730  14040  14400  14810  15390  15740  21420  16460  
 16690  17100  17530);
 
/*      93   94   95   96   97   98   99   00   01   02  03  04 05  06  07  08  09  10  11  12  13 */
retain
 _rt1(   0    0    0    0    0    0    0    0    0   .1  .1 .1  .1  .1  .1  .1  .1  .1  .1  .1  .1)
 _rt2( .15  .15  .15  .15  .15  .15  .15  .15  .15  .15 .15 .15 .15 .15 .15 .15 .15 .15 .15 .15 .15)
 _rt3( .28  .28  .28  .28  .28  .28  .28  .28 .275  .27 .25 .25 .25 .25 .25 .25 .25 .25 .25 .25 .25)
 _rt4( .31  .31  .31  .31  .31  .31  .31  .31 .305  .30 .28 .28 .28 .28 .28 .28 .28 .28 .28 .28 .28)
 _rt5( .36  .36  .36  .36  .36  .36  .36  .36 .355  .35 .33 .33 .33 .33 .33 .33 .33 .33 .33 .33 .33)
 _rt6(.396 .396 .396 .396 .396 .396 .396 .396 .391 .386 .35 .35 .35 .35 .35 .35 .35 .35 .35 .35 .35)
 _rt7(.396 .396 .396 .396 .396 .396 .396 .396 .391 .386 .35 .35 .35 .35 .35 .35 .35 .35 .35 .35 .396);

/*              sngl  joint    sep     hh  widow    sep    */
retain _brk1 (     0      0      0      0      0      0     /*1993*/
                   0      0      0      0      0      0     /*1994*/
                   0      0      0      0      0      0     /*1995*/
                   0      0      0      0      0      0     /*1996*/
                   0      0      0      0      0      0     /*1997*/
                   0      0      0      0      0      0     /*1998*/
                   0      0      0      0      0      0     /*1999*/
                   0      0      0      0      0      0     /*2000*/
                   0      0      0      0      0      0     /*2001*/
                6000  12000   6000  10000   12000  6000     /*2002*/
                7000  14000   7000  10000   14000  7000     /*2003*/
                7150  14300   7150  10200   14300  7150     /*2004*/
                7300  14600   7300  10450   14600  7300     /*2005*/
                7550  15100   7550  10750   15100  7550     /*2006*/
                7825  15650   7825  11200   15650  7825     /*2007*/
                8025  16050   8025  11450   16050  8025     /*2008*/
                8350  16700   8350  11950   16700  8350     /*2009*/
                8375  16750   8375  11950   16750  8375     /*2010*/
                8500  17000   8500  12150   17000  8500     /*2011*/
                8700  17400   8700  12400   17400  8700     /*2012*/
                8925  17850   8925  12750   17850  8925);   /*2013*/


/*              sngl  joint    sep     hh  widow    sep    */
retain _brk2 ( 22100  36900  18450  29600  36900  18450     /*1993*/
               22750  38000  19000  30500  38000  19000     /*1994*/
               23350  39000  19500  31250  39000  19500     /*1995*/
               24000  40100  20050  32150  40100  20050     /*1996*/
               24650  41200  20600  33050  41200  20600     /*1997*/
               25350  42350  21175  33950  42350  21175     /*1998*/
               25750  43050  21525  34550  43050  21525     /*1999*/
               26250  43850  21925  35150  43850  21925     /*2000*/
               27050  45200  22600  36250  45200  22600     /*2001*/
               27950  46700  23350  37450  46700  23350     /*2002*/
               28400  56800  28400  38050  58600  28400     /*2003*/
               29050  58100  29050  38900  58100  29050     /*2004*/
               29700  59400  29700  39800  59400  29700     /*2005*/
               30650  61300  30650  41050  61300  30650     /*2006*/
               31850  63700  31850  42650  63700  31850     /*2007*/
               32550  65100  32550  43650  65100  32550     /*2008*/
               33950  67900  33950  45500  67900  33950     /*2009*/
               34000  68000  34000  45550  68000  34000     /*2010*/
               34500  69000  34500  46250  69000  34500     /*2011*/
               35350  70700  35350  47350  70700  35350     /*2012*/
               36250  72500  36250  48600  72500  36250 );  /*2013*/


/*              sngl  joint    sep     hh  widow    sep    */
retain _brk3 ( 53500  89150  44575  76400  89150  44575     /*1993*/
               55100  91850  45925  78700  91850  45925     /*1994*/
               56550  94250  47125  80750  94250  47125     /*1995*/
               58150  96900  48450  83050  96900  48450     /*1996*/
               59750  99600  49800  85350  99600  49800     /*1997*/
               61400 102300  51150  87700 102300  51150     /*1998*/
               62450 104050  52025  89150 104050  52025     /*1999*/
               63550 105950  52975  90800 105950  52950     /*2000*/
               65550 109250  54625  93650 109250  54625     /*2001*/
               67700 112850  56425  96700 112850  56425     /*2002*/
               68800 114650  57325  98250 114650  57325     /*2003*/
               70350 117250  58625 100500 117250  58625     /*2004*/
               71950 119950  59975 102800 119950  59975     /*2005*/
               74200 123700  61850 106000 123700  61850     /*2006*/
               77100 128500  64250 110100 128500  64250     /*2007*/
               78850 131450  65725 112650 131450  65725     /*2008*/
               82250 137050  68525 117450 137050  68525     /*2009*/
               82400 137300  68650 117650 137300  68650     /*2010*/
               83600 139350  69675 119400 139350  69675     /*2011*/
               85650 142700  71350 122300 142700  71350     /*2012*/
               87850 146400  73200 125450 146400  73200 );  /*2013*/


/*              sngl  joint    sep     hh  widow    sep    */
retain _brk4 (115000 140000  70000 127500 140000  70000     /*1993*/
              115000 140000  70000 127500 140000  70000     /*1994*/
              117950 143600  71800 130800 143600  71800     /*1995*/
              121300 147700  73850 134500 147750  73850     /*1996*/
              124650 151750  75875 138200 151750  75875     /*1997*/
              128100 155950  77975 142000 155950  77975     /*1998*/
              130250 158550  79275 144400 158550  79275     /*1999*/
              132600 161450  80725 147050 161450  80725     /*2000*/
              136750 166500  83250 151650 166500  83250     /*2001*/
              141250 171950  85975 156600 171950  85975     /*2002*/
              143500 174700  87350 159100 174700  87350     /*2003*/
              146750 178650  89325 162700 178650  89325     /*2004*/
              150150 182800  91400 166450 182800  91400     /*2005*/
              154800 188450  94225 171650 188450  94225     /*2006*/
              160850 195850  97925 178350 195850  97925     /*2007*/
              164550 200300 100150 182400 200300 100150     /*2008*/
              171550 208850 104425 190200 208850 104425     /*2009*/
              171850 209250 104625 190550 209250 104625     /*2010*/
              174400 212300 106150 193350 212300 106150     /*2011*/
              178650 217450 108725 198050 217450 108725     /*2012*/
              183250 223050 111525 203150 223050 111525 );  /*2013*/


/*              sngl  joint    sep     hh  widow    sep    */
retain _brk5 (250000 250000 125000 250000 250000 125000     /*1993*/
              250000 250000 125000 250000 250000 125000     /*1994*/
              256500 256500 128250 256500 256500 128250     /*1995*/
              263750 263750 131875 263750 263750 131875     /*1996*/
              271050 271050 135525 271050 271050 135525     /*1997*/
              278450 278450 139225 278450 278450 139225     /*1998*/
              283150 283150 141575 283150 283150 141575     /*1999*/
              288350 288350 144175 288350 288350 144175     /*2000*/
              297350 297350 148675 297350 297350 148675     /*2001*/
              307050 307050 153525 307050 307050 153525     /*2002*/
              311950 311950 155975 311950 311950 155975     /*2003*/
              319100 319100 159550 319100 319100 159550     /*2004*/
              326450 326450 163225 326450 326450 163225     /*2005*/
              336550 336550 168275 336550 336550 168275     /*2006*/
              349700 349700 174850 349700 349700 174850     /*2007*/
              357700 357700 178850 357700 357700 178850     /*2008*/
              372950 372950 186475 372950 372950 186475     /*2009*/
              373650 373650 186825 373650 373650 186825     /*2010*/
              379150 379150 189575 379150 379150 189575     /*2011*/
              388350 388350 194175 388350 388350 194175     /*2012*/
              398350 398350 199175 398350 398350 199175 );  /*2013*/


/*              sngl  joint    sep     hh  widow    sep    */
retain _brk6 (   1e20   1e20   1e20   1e20   1e20   1e20     /*1993*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20    /*1994*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*1995*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*1996*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*1997*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*1998*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*1999*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2000*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2001*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2002*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2003*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2004*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2005*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2006*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2007*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2008*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2009*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2010*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2011*/ 
                 1e20   1e20   1e20   1e20   1e20   1e20     /*2012*/ 
               400000 450000 225000 425000 450000 225000 );  /*2013*/


/*               sngl  joint    sep     hh  widow    sep   dep     */
retain _stded (  3700   6200   3100   5450   6200   3100    600     /*1993*/
                 3800   6350   3175   5600   6350   3175    600     /*1994*/
                 3900   6550   3275   5750   6550   3275    650     /*1995*/
                 4000   6700   3350   5900   6700   3350    650     /*1996*/
                 4150   6900   3450   6050   6900   3450    650     /*1997*/
                 4250   7100   3550   6250   7100   3550    700     /*1998*/
                 4300   7200   3600   6350   7200   3600    700     /*1999*/
                 4400   7350   3675   6450   7350   3675    700     /*2000*/
                 4550   7600   3800   6650   7600   3800    750     /*2001*/
                 4700   7850   3925   6900   7850   3925    750     /*2002*/
                 4750   9500   4750   7000   9500   4750    750     /*2003*/
                 4850   9700   4850   7150   9700   4850    800     /*2004*/
                 5000  10000   5000   7300  10000   5000    800     /*2005*/
                 5150  10300   5150   7550  10300   5150    850     /*2006*/
                 5350  10700   5350   7850  10700   5350    850     /*2007*/
                 5450  10900   5450   8000  10900   5450    900     /*2008*/
		 5700  11400   5700   8350  11400   5700    950     /*2009*/
                 5700  11400   5700   8400  11400   5700    950     /*2010*/
                 5800  11600   5800   8500  11600   5800    950     /*2011*/
                 5950  11900   5450   8700  11900   5450    950     /*2012*/
                 6100  12200   6100   8950  12200   6100   1000  ); /*2013*/




/*              sngl   joint    sep     hh  widow    sep     */
retain _amtex (33750   45000  22500  33750  45000  22500     /*1993*/
               33750   45000  22500  33750  45000  22500     /*1994*/
               33750   45000  22500  33750  45000  22500     /*1995*/
               33750   45000  22500  33750  45000  22500     /*1996*/
               33750   45000  22500  33750  45000  22500     /*1997*/
               33750   45000  22500  33750  45000  22500     /*1998*/
               33750   45000  22500  33750  45000  22500     /*1999*/
               33750   45000  22500  33750  45000  22500     /*2000*/
               35750   49000  24500  35750  49000  24500     /*2001*/
               35750   49000  24500  35750  49000  24500     /*2002*/
               40250   58000  29000  40250  58000  29000     /*2003*/
               40250   58000  29000  40250  58000  29000     /*2004*/
               40250   58000  29000  40250  58000  29000     /*2005*/
               42500   62550  31275  42500  62550  31275     /*2006*/
               44350   66250  33125  44350  66250  33125     /*2007*/
               46200   69950  34975  46200  69950  34975     /*2008*/
               46700   70950  35475  46700  70950  35475     /*2009*/
               47450   72450  36225  47450  72450  36225     /*2010*/
               48450   74450  37225  48450  74450  37225     /*2011*/
               50600   78750  39375  50600  78750  39375     /*2012*/
               51900   80750  40375  51900  80750  40375  ); /*2013*/

/*              sngl  joint     sep     hh  widow    sep    */
retain _exmpb (108450 162700  81350 135650 162700  81350     /*1993*/
               111800 167700  83850 139750 167700  83850     /*1994*/
               114700 172070  86035 143350 172070  86035     /*1995*/
               117950 176950  88475 147450 176950  88475     /*1996*/
               121200 181800  90900 151500 181800  90900     /*1997*/
               124500 186800  93400 155650 186800  93400     /*1998*/
               126600 189950  94975 158300 189950  94975     /*1999*/
               128950 193400  96700 161150 193400  96700     /*2000*/
               132950 199450  99725 166200 199450  99725     /*2001*/
               137300 206000 103000 171650 206000 103000     /*2002*/
               139500 209250 104625 174400 209250 104625     /*2003*/
               142700 214050 107025 178350 214050 107025     /*2004*/
               145950 218950 109475 182450 218950 109475     /*2005*/
               150500 225750 112875 188150 225750 112875     /*2006*/
               156400 234600 117300 195500 234600 117300     /*2007*/
               159950 239950 119975 199950 239950 119975     /*2008*/
               166800 250200 125000 208500 250200 125000     /*2009*/
               166800 250200 125000 208500 250200 125000     /*2010*/
               169950 254350 127300 211950 254350 127300     /*2011*/
               169950 254350 127300 211950 254350 127300     /*2012*/
               200000 300000 150000 250000 300000 150000 );  /*2013*/

retain _amtys  (112500  150000  75000 112500 150000  75000 );
retain _cphase (75000   110000  55000  75000  75000  55000 );
retain _thresx (200000  250000 125000 200000 250000 125000 );
retain _ssb50  (25000   32000      0  25000  25000      0 );
retain _ssb85  (34000   44000      0  34000  34000      0 );


if FLPDYR LT 1993 or FLPDYR GT 2013 then do;
   put "FLPDYR out of bounds for TAXCALC" SOIYR FLPDYR RECID;
   stop;
end;

/* Not all variables are available at all _sites and all years. By setting
   all the input variables to missing in this statement we suppress
   warning messAGES when undefined variables are used in sum statements.
*/
retain %MISC _fixup _ficeic . ;

/* These variables are individual identifiers. Using both a retain and drop
   allows us to drop variables that may not exist every year without
   triggering an exception.
*/


/*All missing dollar values treated as zero */
do over _e; if _e eq . then _e = 0; end;
do over _n; _n = 0; end;
do over _m; if _m eq . then _m = 0; end;

/* Correction for multiply defined E-codes */
if SOIYR in(2001:2003) then _rrcrd = e07960; else _rrcrd = 0;
if SOIYR ge 2009 then _altfuel = e07960; else _altfuel = 0;
if SOIYR eq 2006 then x03200 = e03200; else x03200 = 0;

/* 2 to 4 digit year conversion */
if SOIYR in(1994,1995) then do;
    _DOBYR =  DOBYR+1900; 
   _SDOBYR = SDOBYR+1900; 
end;
else do;
    _DOBYR =  DOBYR;
   _SDOBYR = SDOBYR;
end;

/* Imputations for _exact */ 

_feiexcgt = 0;
if _exact then do;
  if TXST eq 10 and e24516 gt e04800 then _feiexcgt = e05100 - e24580;
  x59560 = _earned;
end;

/* Imputations for _fixup */
if e04800 gt 0 then _totald=max(0,e00100-e04600,e04800,0);

/* Other imputations */
if e00650 eq . and FLPDYR ge 2003 then 
   c00650 = .67*e00600; else c00650 = e00650;
if e04470 gt 0 and e04470 lt _stded{FLPDYR,MARS} then _compitem=1; else _compitem=0; 
if FLPDYR eq 2007 and SOIYR eq 2008 then x07400 = 0; else x07400 = e07400;

/* Imputation for variable changing meaning */
if FLPDYR eq 2005 and SOIYR eq 2006 and e03200 gt 0 then x03150 = e03200; else x03150 = e03150;
x03150 = e03150;


/*Number of children for child tax credit*/
if SOIYR ge 2002 then 
  _nctcr = N24;
else if _chmax{flpdyr} gt 0 then 
  _nctcr = sum(of xtxcr1-xtxcr10);
else
  _nctcr = XOCAH;

/* Imputations for "As Adjusted for AMT" */
array _x x02900 x59560 x60000 x60130 x60240 x60220 x60260 x62720 x62730 
x62740;
do over _x; _x = 0; end;
retain REGION .;
if REGION EQ . then do;
   _puf = 1;
   _cmp = 0;
end;
else do;
   _puf = 0;
   _cmp = 1;
end;

if f6251 and _exact then do;
  x60260 = e60260 - e00700;
  x62720 = e62720 - e24517;
  *if SCHD eq 0 then x62720 = 0;
  x18300 = max(t18300,e18300);
  x18600 = max(t18600,e18600);
  if SCHA then do;
    if FLPDYR in(2009,2010) and _statax ge e18450 then 
       x60240 = e60240 - e18300 + e18600;
    else
       x60240 = e60240 - e18300;
  end;
  x60220 = e60220 - e20800;
  x60820 = e60820 - e19700;
  x60130 = e60130 - e21040;
  x62730 = e62730 - e24515;   
  x62740 = e62740 - e24516;
  x62746 = e62746 - sum(e24532,0);
  x62748 = e62748 - sum(e24583,0);
end;
else do;
  x60260 = 0;
  x62720 = 0;
  x60240 = 0;
  x60220 = 0;
  x60130 = 0;
  x62730 = 0;
  x62740 = 0;
  x62746 = 0;
  x62748 = 0;
  x60820 = 0;
end;

retain exact 1;

%MEND INIT;


/*******************************************
   The following macro does the basic tax 
   calculations and is used to simplify the 
   flow of the tax calculator.
   (macro by James Pearce (OTA), then
   modified by DRF
*******************************************/

%MACRO TAXER(inc_in,inc_out,MAR);
if _exact then do;
  _a1=.;
  _a2=.;
  _a3=.;
  _a4=.;
  _a5=.;
  _a6=.;

/*******************************************************
  The following code approximates tax tables for those 
  with under $100,000 of taxable income
*******************************************************/
  if &inc_in < 3000 then do;
    _a1 = &inc_in / 100;
    _a2 = floor(_a1);
    _a3 = _a2*100;
    _a4 = (_a1-_a2)*100;

    if      _a4 < 25 then _a5 = 13; 
    else if _a4 < 50 then _a5 = 38; 
    else if _a4 < 75 then _a5 = 63; 
    else                  _a5 = 88;

    if &inc_in=0 then _a5=0;
    _a6 = _a3 + _a5;
  end;

  if &inc_in ge 3000 and &inc_in < 100000 then do;
    _a1 = &inc_in / 100;
    _a2 = floor(_a1);
    _a3 = _a2*100;
    _a4 = (_a1-_a2)*100;
  
    if _a4 < 50 then _a5 = 25; 
    else             _a5 = 75;
  
    if &inc_in=0 then _a5=0;
    _a6 = _a3 + _a5;
  end;
  if _a6 = . then _a6 = &inc_in;
end;
else do;
  _a6 = &inc_in;
end;

/*******************************************************
  Calculate tax using specified rate structure 
*******************************************************/
  &inc_out = _rt1{FLPDYR} * min(_a6,_brk1{FLPDYR,MARS})
        +_rt2{FLPDYR} * min(_brk2{FLPDYR,&MAR}-_brk1{FLPDYR,&MAR},max(0.,_a6-_brk1{FLPDYR,&MAR}))
        +_rt3{FLPDYR} * min(_brk3{FLPDYR,&MAR}-_brk2{FLPDYR,&MAR},max(0.,_a6-_brk2{FLPDYR,&MAR}))
        +_rt4{FLPDYR} * min(_brk4{FLPDYR,&MAR}-_brk3{FLPDYR,&MAR},max(0.,_a6-_brk3{FLPDYR,&MAR}))
        +_rt5{FLPDYR} * min(_brk5{FLPDYR,&MAR}-_brk4{FLPDYR,&MAR},max(0.,_a6-_brk4{FLPDYR,&MAR}))
        +_rt6{FLPDYR} * min(_brk6{FLPDYR,&MAR}-_brk5{FLPDYR,&MAR},max(0.,_a6-_brk5{FLPDYR,&MAR}))
        +_rt7{FLPDYR} * max(0.,_a6-_brk6{FLPDYR,MARS}) ;



%MEND TAXER;

%MACRO PRINT6(dataset=);
/*
  This macro prints 6 tax records with each record a column of numbers.
  If the input data is not the PUF, it anonymizes the data by rounding
  dollar amounts to 4 digits, dropping records with any large dollar
  values, or with small  weight. It prints the first 6 records in the
  dataset that pass that filter.
*/
  data puflike;
  set &dataset;
/*  if  DOBYR ne . then do;  
    array e %EVALUES %CVALUES %NBERVARS;
    do over e;
       mag = abs(data);
       if mag gt 500000 then
          delete;
       if mag gt 99999 then
          data = 100*int(data/100);
       else if mag gt 9999 then
          data = 10*int(data/10);
    end;
  if s006 gt 10;
  end;
*/
  run;

  data; /* Print first 6 records */
  set puflike;
  if _n_ le 6;
  run;

  proc transpose out=trans name=var   prefix=R;
  run;

  /* Put fields in order by digits only */
  data;set;
  indexc=indexc(var,'EecTS');
  if indexc(var,"EecTS") and input(substr(var,6,1), ?? 1.) ne . then
       nvar = substr(var,2,5);
     else
       nvar = var;
  run;

  proc sort;by nvar;run;

  data;
  set;
  retain printall 1;
  initial = substr(var,1,1);
  prefix = substr(var,2,2);
  linitial = lag(initial);
  sum = sum(r1,r2,r3,r4,r5,r6,0) ;  
  lsum = lag(sum);
 /* if initial eq "T" and linitial eq "E" and sum eq lsum then delete;
  if initial eq "c" and sum ne lsum then star="*"; else star=" ";
 */ 
 if (sum ne . and sum ne 0) or (prefix eq '24' or prefix eq '62');
  run;

  proc print;
  format r1--r6 8.0;
  id var;
  var r1 r2 r3 r4 r5 r6 /*var*/;
  run;

  data;
  set;
  initial = substr(var,1,1);
  lnvar = lag(nvar);
  sum = sum(r1,r2,r3,r4,r5,r6,0) ;  
  lsum = lag(sum);
  if initial eq "c" and nvar eq lnvar and sum ne lsum;
  output;
  run;

%MEND PRINT6;


