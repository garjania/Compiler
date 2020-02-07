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
	store i32 1, i32* %a
	%b = alloca float
	store float 1.41, float* %b
	%_0 = load i32, i32* %a
	%_1 = load float, float* %b
	%_2 =  sitofp i32 %_0 to float
	%_3 = fadd float %_1, %_2
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.float, i32 0, i32 0), float %_3)
	ret i32 0
}
