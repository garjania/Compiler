@_8 = internal constant [13 x i8] c"not equal ! \00"
@.i32 = private unnamed_addr constant [3 x i8] c"%d\00", align 1
declare i32 @scanf(i8*, ...)
declare i32 @printf(i8*, ...)
define i32 @main()
{
	%a = alloca i32
	store i32 %2, i32* %a
	%b = alloca i32
	store i32 %3, i32* %b
	%c = alloca i32
	%_0 = load i32, i32* %b
	%_1 = load i32, i32* %a
	%_2 = add i32 %_1, %_0
	store i32 %_2, i32* %c
	%_3 = load i32, i32* %c
	%_4 = icmp ne i32 1, %_3
	br i1 %_5, label %_6, label %_7
	_6:
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @_8, i32 0, i32 0)
	br label %_7
	_7:
	ret i32 0
}
