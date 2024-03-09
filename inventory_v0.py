import os
from pathlib import Path

import hashlib

def file_hash(filename):
   # make a hash object
   h = hashlib.sha1()

   # open the file for reading in binary mode
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()



list_formats = [".mp3", ".shn", ".aiff", ".wav", ".m4a", "flac"]

test_dir = r"G:\_Mechen_Muze\Quicksilver Messenger Service"
test_dir = r"G:\_Mechen_Muze\Grateful Dead"

list_audio = [] 

for root, dirs, files in os.walk(test_dir, topdown=False):
   for name in files:
      this_file = os.path.join(root, name)
      for items in list_formats:
         if items in this_file:
            list_audio.append(this_file)
            print(os.path.join(root, name))
            
#   for name in dirs:

# list of tuples of (path_to_audio_file, hash_of_file)
list_tuple_audio = []
list_hashes = []
counter = 0

for items in list_audio:
   files_hash = file_hash(items)
   list_tuple_audio.append( (counter, items, files_hash) )
   print(files_hash)
   list_hashes.append( (counter, files_hash))
   counter += 1
   

print(os.path.join(root, name))
