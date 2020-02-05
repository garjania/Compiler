define void @good([1 x [h2 x float]] %b)
{
	%b = alloca i32
	ret void
}
define i32 @hello()
{
	%c = alloca i32
	%_0 = mul i32 3, 3
	%_1 = call i32 @good(i32 -1,i32 %_0)
	%_2 = xor i1 1, %_1
	%_3 = mul i32 %_3, 3
	store i32 %_3, i32* %c
	br i1 %_4, label %_5, label %_6
	_5:
	%_7 = mul i32 0, 3
	%_8 = call i32 @good(i32 -2,i32 %_7)
	%_9 = mul i32 %_8, 2
	%_10 = add i32 %_9, 3
	store i32 %_10, i32* %c
	_6:
	%_11 = mul i32 %c, %c
	%_12 = add i32 2, %_11
	br i1 %_12, label %_13, label %_14
	_13:
	store i32 1, i32* %c
	br label %_13
	_14:
	ret i32 %c
}
