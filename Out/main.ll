@.i32 = private unnamed_addr constant [3 x i8] c"%d\00", align 1
declare i32 @scanf(i8*, ...)
declare i32 @printf(i8*, ...)
define void @good([1 x [2 x float]] %b)
{
	%a = alloca i32
	store i32 %3, i32* %a
	%d = alloca float
	store float %3.2, float* %d
	%c = alloca float
	%_0 = load i32, i32* %a
	%_1 = load float, float* %d
	%_2 =  sitofp i32 %_0 to float
	%_3 = fmul float %_1, %_2
	store float %_3, float* %c
	ret void
}
