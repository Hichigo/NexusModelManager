import bpy
import sys
import os
from shutil import copyfile
from mathutils import Vector

if __name__ == "__main__":
    append_from_blendfile = sys.argv[5]
    directory_folder = sys.argv[6] # in my case "Collection"
    collection_name = sys.argv[7]
    save_dir = sys.argv[8]
    offset_location = sys.argv[9].split("|") # split string by "|" symbol
    offset_location = Vector( (float(offset_location[0]), float(offset_location[1]), float(offset_location[2])) ) # make vector

    cursor_rotation = sys.argv[10].split("|") # 0 - use or not; 1,2,3 - x,y,z
    if cursor_rotation[0] == "True":
        use_rotation = True
    else:
        use_rotation = False

    pack_data = sys.argv[11]

    save_file = os.path.join(save_dir, collection_name + ".blend")

    filepath = os.path.join(append_from_blendfile, directory_folder, collection_name)
    directory = os.path.join(append_from_blendfile, directory_folder)

    if pack_data == "TEXTURE":
        missing_file = False
        for image in bpy.data.images:
            if image.name != "Render Result":
                image_path = os.path.abspath(image.filepath_from_user())

                if not os.path.isfile(image_path):
                    print("MISSING TEXTURE --> ", image_path)
                    missing_file = True
        
        if missing_file:
            print("------------------ ERROR ------------------")
            print("------------- ASSET NOT SAVED -------------")
            bpy.ops.wm.quit_blender()

    # set 3D cursor to center scene
    bpy.context.scene.cursor.location = Vector((0,0,0))

    # create empty object
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    empty_object = bpy.data.objects["Empty"]
    empty_object.name = collection_name

    # append asset
    bpy.ops.wm.append(filepath=filepath, directory=directory, filename=collection_name, autoselect=True)

    # move all selected objects to center scene
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        obj.location -= offset_location

    # set empty object active
    empty_object.select_set(True)
    bpy.context.window.view_layer.objects.active = empty_object

    # link empty object to collection
    bpy.data.collections[collection_name].objects.link(empty_object)

    # unlink empty object from root collection
    bpy.context.scene.collection.objects.unlink(empty_object)

    # set parent all selected object to empty object
    bpy.ops.object.parent_set(type="OBJECT", keep_transform=False)

    # "offset" rotation
    if use_rotation:
        empty_object.rotation_euler.x -= float(cursor_rotation[1])
        empty_object.rotation_euler.y -= float(cursor_rotation[2])
        empty_object.rotation_euler.z -= float(cursor_rotation[3])

    # increase size asset for border on render icon
    empty_object.scale = Vector((1.2, 1.2, 1.2))

    # set view camera to selected objects
    bpy.ops.view3d.camera_to_view_selected()

    # return asset size to normal
    empty_object.scale = Vector((1, 1 ,1))

    # create path icon
    render_path = os.path.join(save_dir, "render", collection_name + ".png")
    bpy.context.scene.render.filepath = render_path

    # render icon
    bpy.ops.render.render(write_still=True)

    # remove camera
    # bpy.data.objects.remove(bpy.data.objects["Camera"])

    # remove HDRI image
    bpy.data.images.remove(bpy.data.images["tomoco_studio.exr"])

    if pack_data == "PACK":
        bpy.ops.file.pack_all()
    elif pack_data == "TEXTURE":
        # save images to root library
        path_textures = os.path.abspath(os.path.join(save_dir, "../..", "textures"))

        # create folder in not exist
        if not os.path.exists(path_textures):
            os.makedirs(path_textures)

        for image in bpy.data.images:
            if image.name != "Render Result":
                # bpy.context.selected_objects[0].material_slots[0].material.node_tree.nodes[0].image
                # get absolute path image
                image_path = os.path.abspath(image.filepath_from_user())
                # create new path image
                new_image_path = os.path.join(path_textures, image.name)
                # copy image to new path
                copyfile(image_path, new_image_path)
                # set new path image inside blender
                image.filepath = new_image_path
                print("save image to -> ", new_image_path)

    # save file
    bpy.ops.wm.save_as_mainfile(filepath=save_file)
    print("Asset " + collection_name + " Saved!")

    # quit blender
    bpy.ops.wm.quit_blender()