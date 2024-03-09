import os
import sqlite3

def file_hash(filename, chunk_size = 1024):
    import hashlib
    # make a hash object
    h = hashlib.sha1()

    # open the file for reading in binary mode
    with open(filename,'rb') as file:

        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(chunk_size)
            h.update(chunk)

    # return the hex representation of digest
    return h.hexdigest()

def dir_namespace():
    listObj = []
    for items in dir():
        if items[0] != "_":
            listObj.append(items)
    print(listObj)



def obj_introspect(inObj, return_list = False):
    listObj = []
    for items in dir(inObj):
        if items[0] != "_":
            listObj.append(items)
    print(listObj)
    if return_list:
        return listObj
    
class AudioInventory:
    
    def __init__(self, root_directory):
        self.root_directory = root_directory
        self.audiofiles = []

    def inventory_directory(self):
        list_formats = [".mp3", ".shn", ".aiff", ".wav", ".m4a", ".flac"]
        self.audiofiles = []
        for dirpath, dirnames, filenames in os.walk(self.root_directory):
            if "RECYCLE.BIN" in dirpath:
                pass
            else:
                for filename in filenames:
                    for formats in list_formats:
                        if formats in filename:
                            print(filename)
                            full_path =  os.path.join(dirpath, filename)
                            parent_dir = os.path.split(dirpath)[1]
                            thishash = file_hash(full_path)
                            self.audiofiles.append((filename, parent_dir, full_path, formats, thishash))
    
    
    def update_inventory_directory(self, db_file):
        
        list_formats = [".mp3", ".shn", ".aiff", ".wav", ".m4a", ".flac"]
        
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        for dirpath, dirnames, filenames in os.walk(self.root_directory):
            if "RECYCLE.BIN" in dirpath:
                pass
            
            else:
                for filename in filenames:
                    for formats in list_formats:
                        if formats in filename:
                            #  check if in db
                            full_path =  os.path.join(dirpath, filename)
                            c.execute("SELECT * FROM audiofiles WHERE path=?", (full_path,))
                            
                            if not c.fetchone():                            
                                print(filename)
                                #full_path =  os.path.join(dirpath, filename)
                                parent_dir = os.path.split(dirpath)[1]
                                thishash = file_hash(full_path)
                                self.audiofiles.append((filename, parent_dir,
                                                        full_path, formats, thishash))
                                
        conn.close()


    def create_database(self, db_file):
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS audiofiles
                     (name TEXT, parent TEXT, path TEXT PRIMARY KEY, extension TEXT, filehash TEXT)''')
        conn.commit()
        conn.close()

    def output_to_database(self, db_file, OVERWRITE = False):
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        for audiofile in self.audiofiles:
            filename, parent_dir, full_path, formats, filehash = audiofile
            if OVERWRITE:
                c.execute("INSERT INTO audiofiles VALUES (?, ?, ?, ?, ?)", (filename, parent_dir, full_path, formats, filehash))
            else:
                c.execute("SELECT * FROM audiofiles WHERE path=?", (full_path,))
                if not c.fetchone():
                    c.execute("INSERT INTO audiofiles VALUES (?, ?, ?, ?, ?)", (filename, parent_dir, full_path, formats, filehash))
        conn.commit()
        conn.close()

# Example usage:
# root_dir = '/path/to/your/root/directory'
db_file = 'directory_inventory.db'
# inventory = DirectoryInventory(root_dir)
# inventory.inventory_directory()
# inventory.create_database(db_file)
# inventory.output_to_database(db_file)

#root_dir = 'G://_Mechen_Muze'
root_dir = 'K://40_Muze'

list_Muze = ['G://_Mechen_Muze', 'K://40_Muze', 'N://40_Muze', 'X://40_Muze', 'K://40_Muze_Backup', 'E://40_Muze_beetsDB', 'K://40_Muze_dev', 'K://40_Muze_f']

list_Muze3 = ['L://40_Muze_Prime']

list_Muze2 = ['K://42_Muze_MP3', 'H://44_Muze', 'N://44_NuMuze', 'P://45_NuMuzell',
              'N://58_Muze', '64_Muze', '78_NewMuze', 'N://78_NewMuze',
              'N://__________IN_MUZE', 'B://__SORT_MUZE', 'S://_Mechen_Muze', 'P://44_Ulmo//Bert//Muze', 'N://sh_Muze']
list_Muze4 = ['P://44_Ulmo//Bert//Muze', 'N://sh_Muze']
list_Muze5 = ['S://_Mechen_Muze']
#db_file = 'G://directory_inventory.db'
#inventory = AudioInventory(root_dir)
#inventory.inventory_directory()
#inventory.create_database(db_file)
#inventory.output_to_database(db_file)
#print("Squid")

def update_AudioDB(inDir, Overwrite = False):
    
    db_file = 'G://directory_inventory.db'
    inventory = AudioInventory(inDir)
    inventory.inventory_directory()
    #inventory.create_database(db_file)
    inventory.output_to_database(db_file)
    #inventory.update_inventory_directory(db_file)
    print("Squid")
    
for items in list_Muze4:
    update_AudioDB(items)