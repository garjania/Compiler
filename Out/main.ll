@_7 = internal constant [7 x i8] c"hello!\00"
@_5 = internal constant [2 x i8] c"\0A\00"
@_2 = internal constant [17 x i8] c"the number is : \00"
@.i32 = private unnamed_addr constant [3 x i8] c"%d\00", align 1
declare i32 @scanf(i8*, ...)
declare i32 @printf(i8*, ...)
define i32 @product(i32 %a, i32 %b)
{
	%result = alloca i32
	%_0 = mul i32 %b, %a
	store i32 %_0, i32* %result
	%_1 = load i32, i32* %result
	ret i32 %_1
}
define void @print(i32 %input)
{
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([17 x i8], [17 x i8]* @_2, i32 0, i32 0))
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.i32, i32 0, i32 0), i32 %input)
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([2 x i8], [2 x i8]* @_5, i32 0, i32 0))
	ret void
}
define i32 @main()
{
	%a = alloca [7 x i8]*
	store [7 x i8]* getelementptr inbounds ([7 x i8], [7 x i8]* @_7, i32 0), [7 x i8]** %a
	%b = alloca i32
	%c = alloca float
	%_8 = mul i32 7, 2
	%_9 = add i32 %_8, 1
	store i32 %_9, i32* %c
	%d = alloca i32
	store i32 3, i32* %d
	%_10 = load [7 x i8]*, [7 x i8]** %a
	%_12 = alloca i32
	store i32 0, i32* %_12
	br label %_13
	_13:
	%_14 = load i32, i32* %_12
	%_15 = getelementptr [7 x i8], [7 x i8]* %_10, i32 0, i32 %_14
	%_16 = load i8, i8* %_15
	%_17 = icmp ne i8 %_16, 0
	br i1 %_17, label %_18, label %_19
	_18:
	%_20 = load i32, i32* %_12
	%_21 = add nsw i32 %_20, 1
	store i32 %_21, i32* %_12
	br label %_13
	_19:
	store i32 %_21, i32* %b
	%_22 = load i32, i32* %b
	%_23 = load i32, i32* %d
	%_24 = call i32 @product(i32 %_22,i32 %_23)
	call void @print(i32 %_24)
	ret i32 0
}
