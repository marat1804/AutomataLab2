a = [2, 4, 5, 1, 7, 9]
for i in range(len(a)-1):
	for j in range(0, len(a)-1):
		if a[j]<a[j+1]:
			a[j], a[j+1] = a[j+1], a[j]
print(a)