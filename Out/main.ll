@.i32 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.i64 = private unnamed_addr constant [4 x i8] c"%lu\00" 
@.i8 = private unnamed_addr constant [3 x i8] c"%c\00" 
@.double = private unnamed_addr constant [3 x i8] c"%f\00" 
@.i1 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.str = private unnamed_addr constant [3 x i8] c"%s\00" 
declare i32 @scanf(i8*, ...)
declare i32 @printf(i8*, ...)
define i32 @main()
{
	%a = alloca i32
	%b = alloca i32
	%c = alloca i32
	store i32 1, i32* %a
	store i32 2, i32* %b
	store i32 3, i32* %c
	%_0 = load i32, i32* %a
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.i32, i32 0, i32 0), i32 %_0)
	%_2 = load i32, i32* %b
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.i32, i32 0, i32 0), i32 %_2)
	%_4 = load i32, i32* %c
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.i32, i32 0, i32 0), i32 %_4)
}
