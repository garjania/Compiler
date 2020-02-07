@_8 = internal constant [13 x i8] c"not equal ! \00"
@.i32 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.i8 = private unnamed_addr constant [3 x i8] c"%c\00" 
@.i64 = private unnamed_addr constant [3 x i8] c"%f\00" 
@.i1 = private unnamed_addr constant [3 x i8] c"%d\00" 
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
	%_2 = sdiv i32 %_1, %_0
	%_3 =  sitofp i32 %_2 to float
	store float%_3, float* %_2
	%_4 = load float, float* %c
	%_5 = icmp ne i32 1, %_4
	br i1 %_5, label %_6, label %_7
	_6:
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @_8, i32 0, i32 0))
	br label %_7
	_7:
	ret i32 0
}
