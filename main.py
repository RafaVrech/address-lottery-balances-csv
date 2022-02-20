from numba import cuda
from utils import *
from kernel import *
import atexit

#########################################################
####################### PARAMS ##########################
#########################################################
blocks_per_grid = 184
threads_per_block = 128

pk_range_step = 3
pk_range_start = 10000
pk_range_end = 115792089237316195423570985008687907852837564279074904382605163141518161494336

csv_file_path = './files/btc_balance_sorted.csv'
# csv_file_path = './files/testcsv.csv'
private_keys_state_file_path = './files/private_keys_state.txt'
results_file_path = "./files/matches.txt"
#-------------------------------------------------------#

#########################################################
######################## FILES ##########################
#########################################################
file_private_keys_state = open(private_keys_state_file_path, "a+")
file_results = open(results_file_path, "a")

def close_files():
  file_private_keys_state.close()
  file_results.close()
  
atexit.register(close_files)
#-------------------------------------------------------#

print("\n ------ Start run ------ ")

while(pk_range_start < pk_range_end):
  # create array with addresses 
  initial_array = create_array_input(file_private_keys_state, pk_range_step, pk_range_start)

  csv_array = iter_loadtxt(csv_file_path, skiprows=1)

  # copy stuff to GPU
  device_in = cuda.to_device(initial_array)
  device_csv_in = cuda.to_device(csv_array)
  device_out = cuda.device_array(pk_range_step, dtype='U34')

  # run the kernel
  gpu_kernel[blocks_per_grid, threads_per_block](device_in, device_csv_in, device_out)

  # wait for all threads to complete
  cuda.synchronize()

  # copy the output array back to the host system
  out_result = device_out.copy_to_host()

  # Save to file which generated addresses matched with an address with balance
  file_results.write(str(out_result))

  # Print which generated addresses matched with an address with balance
  printStuff("Result", device_out.copy_to_host())
  
  # Overide the state
  file_private_keys_state.write(pk_range_start)
