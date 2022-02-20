import numpy as np
from numba import cuda
#import code
#code.interact(local=locals)
# to measure exec time
from timeit import default_timer as timer

# normal function to run on cpu
def func():							
	for i in range(10000000):
		print("CPU", i)

# function optimized to run on gpu
@cuda.jit						
def func2():
	index = blockIdx.x * blockDim.x + threadIdx.x

if __name__=="__main__":
	threadsperblock = 32 
	blockspergrid = (10000000 + (threadsperblock - 1))
	
	start = timer()
	func()
	print("without GPU:", timer()-start)
	
	start = timer()
	func2[blockspergrid, threadsperblock]()
	print("with GPU:", timer()-start)

32 trheads
48 blocks