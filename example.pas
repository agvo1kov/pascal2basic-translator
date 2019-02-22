Program example;
var
	a, b: integer;
    abc: array [1..10+(1),5..6] of integer;
    abc1: array [1 .. 3] of integer; 
    ccc: array ['a' .. 'b'] of integer;
    c: real;
    s, d: string;
label iteration, out;
begin
	a := 0;
    s := (''+'Hello');
    s := s + ', world!';
    c := 0.005;
    d:='';
    abc[11 + 0- 1,5]:=5+6;

        { comment }

	iteration:
	if (a>5+1)then
		goto out
	else
		a :=a+1;
        b:= -1* 1- 0;
        s:='a'+'b';
	goto iteration;
    
    c :=1.2e+76;

	out:
end.






{function factorial(n: integer): integer;
var
    a: integer;
begin
  if n>1 then
    factorial:=n*factorial(n-1)
  else
    factorial:=1;
    end;
    
    
    function factorial(n: integer): integer;
procedure abss;
begin
    writeln();
end;
var
    a: integer;
begin
  if n>1 then
    factorial:=n*factorial(n-1)
  else
    factorial:=1;
    end;}