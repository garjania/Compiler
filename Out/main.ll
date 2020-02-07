@_9 = internal constant [13 x i8] c"not equal ! \00"
@.i32 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.i8 = private unnamed_addr constant [3 x i8] c"%c\00" 
@.i64 = private unnamed_addr constant [3 x i8] c"%f\00" 
@.i1 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.str = private unnamed_addr constant [3 x i8] c"%s\00" 
declare i32 @scanf(i8*, ...)
declare i32 @printf(i8*, ...)
define i32 @main()
{
	%a = alloca i32
	store i32 2, i32* %a
	%b = alloca i32
	store i32 3, i32* %b
	%c = alloca i32
	%_0 = load i32, i32* %b
	%_1 = load i32, i32* %a
	%_2 = sdiv i32 %_1, %_0
	store i32 %_2, i32* %c
	%_3 = load i32, i32* %c
	%_4 =  zext i32 1 to i64
	%_5 =  zext i32 %_3 to i64
	%_6 = icmp ne i64 %_4, %_5
	br i1 %_6, label %_7, label %_8
	_7:
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @_9, i32 0, i32 0))
	br label %_8
	_8:
	ret i32 0
}
