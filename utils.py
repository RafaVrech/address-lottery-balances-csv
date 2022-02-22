import codecs
import hashlib
from posixpath import split
import ecdsa
import numpy as np
from sqlalchemy import BigInteger
import os
import csv
import requests

def private_key_to_public_key(private_key):
  # Hex decoding the private key to bytes using codecs library
  private_key_bytes = codecs.decode(str(private_key).zfill(64), 'hex')
  # Generating a public key in bytes using SECP256k1 & ecdsa library
  public_key_raw = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
  public_key_bytes = public_key_raw.to_string()
  # Hex encoding the public key from bytes
  public_key_hex = codecs.encode(public_key_bytes, 'hex')
  # Bitcoin public key begins with bytes 0x04 so we have to add the bytes at the start
  public_key = (b'04' + public_key_hex).decode("utf-8")
  # Checking if the last byte is odd or even
  if (ord(bytearray.fromhex(public_key[-2:])) % 2 == 0):
      public_key_compressed = '02'
  else:
      public_key_compressed = '03'
      
  # Add bytes 0x02 to the X of the key if even or 0x03 if odd
  public_key_compressed += public_key[2:66]
  # Converting to bytearray for SHA-256 hashing
  hex_str = bytearray.fromhex(public_key_compressed)
  sha = hashlib.sha256()
  sha.update(hex_str)
  sha.hexdigest() # .hexdigest() is hex ASCII
  rip = hashlib.new('ripemd160')
  rip.update(sha.digest())
  return rip.hexdigest()

chunk_size = 256
def download_dump(csv_file_path):
  url = 'https://bitkeys.work/btc_balance_sorted.csv'
  
  progress = 0
  with requests.get(url, stream=True) as r:
    downloaded_file = open(csv_file_path, "wb")
    content_length = r.headers['Content-Length']
    for chunk in r.iter_content(chunk_size=chunk_size):
      print('Downloading csv: (' +  str(progress) + '/' + str(content_length) + ')', end='\r')
      progress += chunk_size
      if chunk:
          downloaded_file.write(chunk)
          
  #Another way of downlioading the file
  # with open(os.path.split(csv_file_path)[1], 'wb') as f, \
  #         requests.get(url, stream=True) as r:
  #     print(r.headers)
  #     lines = r.iter_lines()
  #     number_of_rows = len(lines)
  #     for line, i in lines:
  #       print('Downloading csv: (' + i + '/' + number_of_rows + ')', end="\r")
  #       f.write(line+'\n'.encode())

def load_csv(file_path, delimiter=',', skiprows=0, dtype='U40'):
  def iter_func():
    if(not os.path.exists(file_path)):
      download_dump(file_path)
    
    with open(file_path, 'r') as infile:
      
      for _ in range(skiprows):
          next(infile)
      for line in infile:
        if(line[0] == '1'):
          split_line = line.rstrip().split(delimiter)
          for column in split_line:
            yield column
    load_csv.rowlength = len(split_line)

    data = np.fromiter(iter_func(), dtype=dtype)
    data = data.reshape((-1, load_csv.rowlength))
    return data
  
  
def load_csv_to_set(file_path, delimiter=',', skiprows=0, dtype='U40'):
  csv_array_set = set()
  if(not os.path.exists(file_path)):
    download_dump(file_path)
  
  with open(file_path, 'r') as infile:
    for _ in range(skiprows):
        next(infile)
    for line in infile:
      if(line[0] == '1'):
        split_line = line.rstrip().split(delimiter)[2]
        csv_array_set.add(split_line)
          
    return csv_array_set

def printStuff(text, toPrint):
  print(">" + text + ("", " (size=" + str(toPrint.size) + ")")[isinstance(toPrint, np.ndarray)])
  print (toPrint)
  print("<" + text)
  print()
  
def create_array_input(pk_range_step, pk_range_start):
  initial_array = np.array([], dtype='U40')
  pk = pk_range_start
  for _ in range(pk_range_step):
    address_ridemp160 = private_key_to_public_key(pk)
    initial_array = np.append(initial_array, np.array([address_ridemp160], dtype='U40'))
    pk += 1
  return initial_array
