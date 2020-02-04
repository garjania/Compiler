define i32 @hello()
{
	%b = alloca i32
	%_0 = mul i32 4, 2
	%_1 = add i32 %_0, 3
	store i32 %_1, i32* %b
}
