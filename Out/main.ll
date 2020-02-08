@.i32 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.i64 = private unnamed_addr constant [4 x i8] c"%lu\00" 
@.i8 = private unnamed_addr constant [3 x i8] c"%c\00" 
@.double = private unnamed_addr constant [4 x i8] c"%lf\00" 
@.i1 = private unnamed_addr constant [3 x i8] c"%d\00" 
@.str = private unnamed_addr constant [3 x i8] c"%s\00" 
declare i32 @scanf(i8*, ...)
declare i32 @printf(i8*, ...)
define i32 @main()
{
	%r = alloca double
	%_0 = load double, double* %r
	call i32 (i8*, ...) @scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.double, i32 0, i32 0), double* %r)
	%_2 = load double, double* %r
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.double, i32 0, i32 0), double %_2)
	ret i32 0
}
