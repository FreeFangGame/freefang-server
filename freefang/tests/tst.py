class A:
	order = 1
class B:
	order = 2


x = [B,A]
x.sort(key=lambda a:a.order)
for i in x:
	print(x)



