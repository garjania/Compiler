@_18 = internal constant [13 x i8] c"not equal ! \00"
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
	%_7 =  zext i32 %_0 to i64
	%_8 =  sitofp i64 %_7 to float
	%_9 = fdiv float %_6, %_8
	%_10 =  fptosi float %_9 to i64
	%_11 =  trunc i64 %_10 to i32
	asdfasdfs
	store i32 %_11, i32* %_0
	%_12 = load float, float* %c
	%_13 =  zext i32 1 to i64
	%_14 =  fptosi float %_12 to i64
	%_15 = icmp ne i64 %_13, %_14
	br i1 %_15, label %_16, label %_17
	_16:
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @_18, i32 0, i32 0))
	br label %_17
	_17:
	ret i32 0
}
