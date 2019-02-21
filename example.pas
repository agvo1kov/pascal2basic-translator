Program example;
var
	a    : integer;
    s : string;
begin
	a := 0;
    s := 'Yes, I am gonna be a      star! Aha-aha!';
    s := s + ', world!';

	iteration:
	if a > 5 then
		goto out
	else
		a := a + 1;
	goto iteration;

	out:
end.
