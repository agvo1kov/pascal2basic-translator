PrOgram Testovaya;

var b,c,d:integer;
	a, e,f,g:real;
	s1, s2, s3,s4:string;
	super_array: array [1..3, 10..20] of integer;
	z: real;
	kk: array [1..2] of string;

LABEL m;

const 
	Pi = 3.14;
	Alpha = 332.1;
	Betta = 4;



begin
a := 5e+11;
a := 5.e+11;
 a := .5e+11;
   a := 5e11;
   a := 5e-11;
   a := 5.234e11;
  a := 5.e-11;
		  a := .5e11;
a := .5;
    a := 2.5;
    a := 5.;
   a:=5^4;
  if a>=34 then
  	begin
  		if a<=20 then
  			if a=10 then
  				a:=1
  			else
  				a:=2;
  	end;

if a<>32 then GOTO m;
a:=31;
m:
	a:=32;

end.