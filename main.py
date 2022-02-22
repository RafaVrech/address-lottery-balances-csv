from audioop import add
from numbers import Number
from this import d
import numba
from utils import *
from kernel import *
import atexit
import sys
import joblib

#########################################################
####################### PARAMS ##########################
#########################################################
blocks_per_grid = 184
threads_per_block = 128

pk_range_step = 10000
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
# file_private_keys_state = open(private_keys_state_file_path, "w+")
file_results = open(results_file_path, "a")

def close_files():
  # file_private_keys_state.close()
  file_results.close()
  
atexit.register(close_files)
#-------------------------------------------------------#
csv_set = load_csv_to_set(csv_file_path, skiprows=1)

print("\n ------ Start run ------ ")

while(pk_range_start < pk_range_end):
  
  f = open(private_keys_state_file_path, "r")
  private_keys_state = f.readline()
  f.close()
  
  if(private_keys_state != ''):
    pk_range_start = int(private_keys_state)
    
  print("\n ------ Run " + str(pk_range_start) + "->" + str(pk_range_start + pk_range_step) + " run ------ ")

  # # create array with addresses 
  initial_array = create_array_input(pk_range_step, pk_range_start)

  initial_array_set = set()
  for row in initial_array:
    initial_array_set.add(row)
  
  # initial_array_set.add('853b0691f07db7fda89618b82abd610292983ee7')
  
  result = (csv_set & initial_array_set)
  if(result != set()):
    file_results.write(str(result) + "In range:" + str(pk_range_start) + "->" + str(pk_range_start + pk_range_step) + '\n')
    file_results.flush()
 
  # print(initial_array_set & csv_array_set)
  
  # copy stuff to GPU
  # device_in = cuda.to_device(initial_array)
  # device_csv_in = cuda.to_device(csv_set)
  # device_out = cuda.device_array(pk_range_step, dtype='U40')

  # run the kernel
  # gpu_kernel[blocks_per_grid, threads_per_block](device_in, device_csv_in, device_out)

  # wait for all threads to complete
  # cuda.synchronize()

  # copy the output array back to the host system
  # out_result = device_out.copy_to_host()

  # Save to file which generated addresses matched with an address with balance
  # file_results.write(str(result))

  # Print which generated addresses matched with an address with balance
  # printStuff("Result", device_out.copy_to_host())
  
  # Overide the state
  f = open(private_keys_state_file_path, "w")
  f.write(str(pk_range_start + pk_range_step))
  f.close()
