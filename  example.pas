Program example;
var
	a: integer;
begin
	a := 0;

	iteration:
	if a > 5 then
		goto out
	else
		a := a + 1;
	goto iteration;

	out:
end.