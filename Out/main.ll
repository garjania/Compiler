@_0 = internal constant [6 x i8] c"hello\00"
define void @good([1 x [2 x float]] %b)
{
	%b = alloca i32
	ret void
}
define i32 @main()
{
	%f = alloca [   x i8]
	store i32 %hello, i32* %f
	%b = alloca [2 x i32]
	%c = alloca i32
	%d = alloca i32, i32 1
	store i32 2, i32* %c
	%_2 = mul i32 2, 3
	%_3 = getelementptr i32, i32* %d, i32 0
	%_4 = add i32 %_3, %_2
	store i32 %_4, i32* %d
	store i32 1, i32* %_1
}
