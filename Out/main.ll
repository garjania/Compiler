define void @good([1 x [2 x float]] %b)
{
	%b = alloca i32
	ret void
}
define i32 @main()
{
	%b = alloca [2 x i32]
	%c = alloca i32
	%d = alloca i32
	%_0 = getelementptr i32, i32* %b, i32 0, i32 1
	store i32 2, i32* %c
	%_1 = mul i32 2, 3
	store i32 %_1, i32* %d
	store i32 1, i32* %_0
}
