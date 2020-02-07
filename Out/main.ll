@_3 = internal constant [2 x i8] c"\0A\00"
@_0 = internal constant [17 x i8] c"the number is : \00"
@.i32 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.i8 = private unnamed_addr constant [3 x i8] c"%c\00" 
@.i64 = private unnamed_addr constant [3 x i8] c"%f\00" 
@.i1 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.str = private unnamed_addr constant [3 x i8] c"%s\00" 
declare i32 @scanf(i8*, ...)
declare i32 @printf(i8*, ...)
define void @print(i32 %input)
{
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([17 x i8], [17 x i8]* @_0, i32 0, i32 0))
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.i32, i32 0, i32 0), i32 %input)
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([2 x i8], [2 x i8]* @_3, i32 0, i32 0))
	ret void
}
define i32 @main()
{
	%index = alloca i32
	store i32 0, i32* %index
	br label %_5
	_5:
	%_6 = load i32, i32* %index
	%_7 =  zext i32 20 to i64
	%_8 =  zext i32 %_6 to i64
	%_9 = icmp ne i64 %_7, %_8
	br i1 %_9, label %_10, label %_11
	_10:
	%_12 = load i32, i32* %index
	call void @print(i32 %_12)
	%_14 = load i32, i32* %index
	%_15 =  zext i32 1 to i64
	%_16 =  sitofp i64 %_15 to float
	%_17 =  zext i32 %_14 to i64
	%_18 =  sitofp i64 %_17 to float
	%_19 = fadd float %_16, %_18
	%_20 =  zext i32 %_14 to i64
	%_21 =  sitofp i64 %_20 to float
	%_22 = fadd float %_19, %_21
	%_23 =  fptosi float %_22 to i64
	%_24 =  trunc i64 %_23 to i32
	store i32 %_24, i32* %_14
	br label %_5
	_11:
	ret i32 0
}
