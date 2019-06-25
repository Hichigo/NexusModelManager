import bpy
from bpy.types import Operator

import subprocess
import os

class VIEW3D_OT_CreateAsset(Operator):
    """Create .blend file and render icon"""
    bl_idname = "view3d.create_asset_path"
    bl_label = "Overwrite file?"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Really?")

    def invoke(self, context, event):

        if not os.path.isfile(bpy.data.filepath):
            self.report({"ERROR"}, "Please save the file!")
            return {"FINISHED"}

        nexus_model_SCN = context.scene.nexus_model_manager

        library_dir = context.window_manager.nexus_model_manager_dir_resource #nexus_model_SCN.create_asset_dir
        library_name = None
        category_name = None
        collection_name = nexus_model_SCN.new_collection_name

        library_name = nexus_model_SCN.library_list
        category_name = nexus_model_SCN.category_list

        file_check = os.path.join(library_dir, library_name, category_name, collection_name, collection_name + ".blend")
        if os.path.isfile(file_check):
            return context.window_manager.invoke_confirm(self, event)

        return self.execute(context)

    def execute(self, context):
        nexus_model_SCN = context.scene.nexus_model_manager

        library_dir = context.window_manager.nexus_model_manager_dir_resource #nexus_model_SCN.create_asset_dir
        library_name = None
        category_name = None
        collection_name = nexus_model_SCN.new_collection_name
        open_blend_file = nexus_model_SCN.render_scenes

        library_name = nexus_model_SCN.library_list
        category_name = nexus_model_SCN.category_list

        asset_dir_path = os.path.join(library_dir, library_name, category_name, collection_name)
        print(asset_dir_path)
        if not os.path.exists(asset_dir_path):
            os.makedirs(asset_dir_path)
            render_path = os.path.join(asset_dir_path, "render")
            os.mkdir(render_path)
            self.report({"INFO"}, "Dirs created: " + asset_dir_path)
        else:
            self.report({"INFO"}, "Dirs already exist" + asset_dir_path)

        collection = None

        if not collection_name in bpy.data.collections:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
        else:
            collection = bpy.data.collections[collection_name]

        # link selected objects to new collection
        selected_objects = context.selected_objects
        for obj in selected_objects:
            collection.objects.link(obj)

        # save file
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

        addons_folder = bpy.utils.user_resource("SCRIPTS", "addons")
        addon_path = os.path.join(addons_folder, "NexusModelManager")
        
        append_from_blendfile = bpy.data.filepath

        tools = os.path.join(addon_path, "tools", "create_asset.py")

        # get cursor location and roration
        cursor_location = bpy.context.scene.cursor.location.copy()
        cursor_rotation = bpy.context.scene.cursor.rotation_euler.copy()

        cursor_location = "{}|{}|{}".format(cursor_location.x, cursor_location.y, cursor_location.z)
        cursor_rotation = "{}|{}|{}|{}".format(nexus_model_SCN.apply_cursor_rotation, cursor_rotation.x, cursor_rotation.y, cursor_rotation.z)

        # prepeare pack_data variable
        pack_data = nexus_model_SCN.pack_data

        sub = subprocess.Popen(
            [
                bpy.app.binary_path,   # path to blender.exe
                open_blend_file,       # open file
                "-b",                  # open background blender
                "--python",
                tools,                 # path to python script
                append_from_blendfile, # from blendfile append collection
                "Collection",
                collection.name,       # append collection name
                asset_dir_path,        # path save this file
                cursor_location,       # cursor location it is pivot point new asset
                cursor_rotation,       # cursor rotation to new asset
                pack_data             # None or pack file to blend file or save textures to root library
            ]
        )

        bpy.data.collections.remove(bpy.data.collections[collection_name])

        return {"FINISHED"}