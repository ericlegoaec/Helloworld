import os
import glob
def os_walk(input_dir):
	for fs_obj in glob.iglob(os.path.join(input_dir, "*")):
		if os.path.isdir(fs_obj):
			os_walk(os.path.join(fs_obj))
		else:
			print (fs_obj)
	return

# os_walk("/Users/frederickli/Projects/HTI")

def foo(x = []):
	x.append(0)
	print (x)

l = [1,2,3]
t = (4,5,6)
d = {'a':7,'b':8,'c':9}

print (*l)