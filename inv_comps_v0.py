import os
import sqlite3


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
    
class DirectoryInventory:
    def __init__(self, root_directory):
        self.root_directory = root_directory
        self.directories = []

    def inventory_directory(self):
        self.directories = []
        for dirpath, dirnames, filenames in os.walk(self.root_directory):
            for dirname in dirnames:
                self.directories.append((dirname, os.path.join(dirpath, dirname)))

    def create_database(self, db_file):
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS directories
                     (name TEXT PRIMARY KEY, path TEXT)''')
        conn.commit()
        conn.close()

    def output_to_database(self, db_file):
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        for directory in self.directories:
            directory_name, directory_path = directory
            c.execute("SELECT * FROM directories WHERE name=?", (directory_name,))
            if not c.fetchone():
                c.execute("INSERT INTO directories VALUES (?, ?)", (directory_name, directory_path))
        conn.commit()
        conn.close()

# Example usage:
# root_dir = '/path/to/your/root/directory'
# db_file = 'directory_inventory.db'
# inventory = DirectoryInventory(root_dir)
# inventory.inventory_directory()
# inventory.create_database(db_file)
# inventory.output_to_database(db_file)

root_dir = 'G://'
db_file = 'G://directory_inventory.db'
inventory = DirectoryInventory(root_dir)
inventory.inventory_directory()
inventory.create_database(db_file)