import bpy
import sys
import os
from shutil import copyfile
from mathutils import Vector

if __name__ == "__main__":
    append_from_blendfile = sys.argv[4]
    directory_folder = sys.argv[5] # in my case "Object"
    objects_name = sys.argv[6].split("|")

    for name in objects_name:

        filepath = os.path.join(append_from_blendfile, directory_folder, name)
        directory = os.path.join(append_from_blendfile, directory_folder)

        print(filepath)
        print(directory)
        print(append_from_blendfile)
        print(directory_folder)
        print(name)
        # append asset
        bpy.ops.wm.append(filepath=filepath, directory=directory, filename=name, autoselect=True)

    print("name")
    bpy.ops.wm.save_as_mainfile(filepath="C:\\Users\\hichi\\Desktop\\asd.blend")