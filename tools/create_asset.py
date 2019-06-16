import bpy
import sys
import os
from mathutils import Vector

if __name__ == "__main__":
    append_from_blendfile = sys.argv[5]
    directory_folder = sys.argv[6] # in my case "Collection"
    collection_name = sys.argv[7]
    save_dir = sys.argv[8]
    offset_location = sys.argv[9].split("|") # split string by "|" symbol
    offset_location = Vector( (float(offset_location[0]), float(offset_location[1]), float(offset_location[2])) ) # make vector

    cursor_rotation = sys.argv[10].split("|") # 0 - use or not; 1,2,3 - x,y,z
    use_rotation = bool(cursor_rotation[0])

    save_file = os.path.join(save_dir, collection_name + ".blend")

    filepath = os.path.join(append_from_blendfile, directory_folder, collection_name)
    directory = os.path.join(append_from_blendfile, directory_folder)

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

    # save file
    bpy.ops.wm.save_as_mainfile(filepath=save_file)

    # quit blender
    bpy.ops.wm.quit_blender()