import bpy
import sys
import os

if __name__ == '__main__':
    append_from_blendfile = sys.argv[5]
    directory_folder = sys.argv[6] # in my case "Collection"
    collection_name = sys.argv[7]
    save_dir = sys.argv[8]

    save_file = os.path.join(save_dir, collection_name + ".blend")

    filepath = os.path.join(append_from_blendfile, directory_folder, collection_name)
    directory = os.path.join(append_from_blendfile, directory_folder)

    bpy.ops.wm.append(filepath=filepath, directory=directory, filename=collection_name, autoselect=True)

    # save file
    bpy.ops.wm.save_as_mainfile(filepath=save_file)

    # quit blender
    bpy.ops.wm.quit_blender()