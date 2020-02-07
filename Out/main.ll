@_13 = internal constant [13 x i8] c"not equal ! \00"
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
	%c = alloca float
	%_0 = load i32, i32* %b
	%_1 = load i32, i32* %a
	%_2 =  zext i32 %_1 to i64
	%_3 =  sitofp i64 %_2 to float
	%_4 =  zext i32 %_0 to i64
	%_5 =  sitofp i64 %_4 to float
	%_6 = fdiv float %_3, %_5
	store float %_6, float* %c
	%_7 = load float, float* %c
	%_8 =  zext i32 1 to i64
	%_9 =  fptosi float %_7 to i64
	%_10 = icmp ne i64 %_8, %_9
	br i1 %_10, label %_11, label %_12
	_11:
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @_13, i32 0, i32 0))
	br label %_12
	_12:
	ret i32 0
}
