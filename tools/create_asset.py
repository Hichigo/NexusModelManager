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

    # create empty object
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    empty_object = bpy.data.objects['Empty']
    empty_object.name = collection_name

    # append asset
    bpy.ops.wm.append(filepath=filepath, directory=directory, filename=collection_name, autoselect=True)

    # set empty object active
    empty_object.select_set(True)
    bpy.context.window.view_layer.objects.active = empty_object

    # link empty object to collection
    bpy.data.collections[collection_name].objects.link(empty_object)

    # unlink empty object from root collection
    bpy.context.scene.collection.objects.unlink(empty_object)

    # set parent all selected object to empty object
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

    # set view camera to selected objects
    bpy.ops.view3d.camera_to_view_selected()

    # create path icon
    render_path = os.path.join(save_dir, "render", collection_name + ".png")
    bpy.context.scene.render.filepath = render_path

    # render icon
    bpy.ops.render.render(write_still=True)

    # remove camera
    bpy.data.objects.remove(bpy.data.objects['Camera'])

    # save file
    bpy.ops.wm.save_as_mainfile(filepath=save_file)

    # quit blender
    bpy.ops.wm.quit_blender()