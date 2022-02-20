from numba import cuda

# Compare list of addresses received with csv array and add to out-array if matches
@cuda.jit
def gpu_kernel(device_in, csv_pub_keys, device_out):
  
  cuda_index = cuda.grid(1)
  current_public_key = device_in[cuda_index]
  
  for csv_pub_key in csv_pub_keys:
    if current_public_key == csv_pub_key[2]:
      device_out[cuda_index] = current_public_key