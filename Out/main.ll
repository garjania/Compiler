@.str = private unnamed_addr constant [3 x i8] c"%d ", align 1
declare i32 @scanf(i8*, ...)
declare i32 @printf(i8*, ...)
define void @good([1 x [2 x float]] %b)
{
	%b = alloca i32
	%_0 = mul i32 3, 2
	store i32 %_0, i32* %b
	ret void
}
define i32 @s(i32 %x, i32 %u)
{
	%n = alloca i32
	ret i32 %n
}
define i32 @hello()
{
	%b = alloca [2 x [3 x [4 x i32]]]
	%a = alloca i32
	%-_1 = getelementptr i32, i32* %b, i32 0, i32 1, i32 1, i32 1
	%-_2 = load i32, i32* %-_1
	%-_3 = sub i32 0, %-_2
	store i32 %-_3, i32* %a
	%-_4 = getelementptr i32, i32* %good, i32 0
	%-_5 = load i32, i32* %-_4
	%-_6 = xor i1 1, %-_5
	%_7 = mul i32 0, 3
	%_8 = call i32 @-_6(i32 %_7,i32 -2,i32 %_7)
	%_9 = xor i1 1, %_8
	%_10 = add i32 %_10, 3
	store i32 %_10, i32* %a
}
