import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty

import subprocess
import os

from .. functions import get_addon_dir, get_addon_prefs
from .. enum_preview_utils import make_category_list, make_library_list

class VIEW3D_OT_CreateAsset(Operator):
    """Create .blend file and render icon"""
    bl_idname = "view3d.create_asset_path"
    bl_label = "Overwrite file?"

    def invoke(self, context, event):
        if not os.path.isfile(bpy.data.filepath):
            self.report({"ERROR"}, "Please save the file!")
            return {"FINISHED"}

        nexus_model_SCN = context.scene.nexus_model_manager

        addon_prefs = get_addon_prefs()
        library_dir = addon_prefs.library_list
        library_name = nexus_model_SCN.library_list
        category_name = nexus_model_SCN.category_list
        collection_name = nexus_model_SCN.new_collection_name

        if bpy.data.collections.find(collection_name) != -1:
            self.report({"ERROR"}, "delete the collection '{}' before creating the asset".format(collection_name))
            return {"FINISHED"}

        file_check = os.path.join(library_dir, library_name, category_name, collection_name, collection_name + ".blend")
        if os.path.isfile(file_check):
            return context.window_manager.invoke_confirm(self, event)

        return self.execute(context)

    def execute(self, context):
        nexus_model_SCN = context.scene.nexus_model_manager

        addon_prefs = get_addon_prefs()
        library_dir = addon_prefs.library_list
        library_name = None
        category_name = None
        collection_name = nexus_model_SCN.new_collection_name
        open_blend_file = nexus_model_SCN.render_scenes

        library_name = nexus_model_SCN.new_library_name
        category_name = nexus_model_SCN.new_category_name

        asset_dir_path = os.path.join(library_dir, library_name, category_name, collection_name)

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

        addon_path = get_addon_dir()
        
        append_from_blendfile = bpy.data.filepath

        tools = os.path.join(addon_path, "resources", "tools", "create_asset.py")

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

class VIEW3D_OT_SetNewLibrary(Operator):
	bl_idname = "view3d.set_new_library"
	bl_label = "Set New Library"
	bl_property = "search_new_library"

	search_new_library: EnumProperty(
		name="Search New Library",
		items=make_library_list,
	)

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {"RUNNING_MODAL"}

	def execute(self, context):
		nexus_model_SCN = context.scene.nexus_model_manager
		nexus_model_SCN.new_library_name = self.search_new_library
		return {'FINISHED'}

class VIEW3D_OT_SetNewCategory(Operator):
	bl_idname = "view3d.set_new_category"
	bl_label = "Set New Category"
	bl_property = "search_new_category"

	search_new_category: EnumProperty(
		name="Search New Category",
		items=make_category_list,
	)

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {"RUNNING_MODAL"}

	def execute(self, context):
		nexus_model_SCN = context.scene.nexus_model_manager
		nexus_model_SCN.new_category_name = self.search_new_category
		return {'FINISHED'}

class VIEW3D_OT_OpenInNewFile(Operator):
    """Open selected objects in new clear .blend file"""
    bl_idname = "view3d.open_in_new_file"
    bl_label = "Overwrite file?"

    def invoke(self, context, event):
        if not os.path.isfile(bpy.data.filepath):
            self.report({"ERROR"}, "Please save the file!")
            return {"FINISHED"}
        
        if len(context.selected_objects) == 0:
            self.report({"ERROR"}, "Please select any object!")
            return {"FINISHED"}
        
        return self.execute(context)

    def execute(self, context):
        nexus_model_SCN = context.scene.nexus_model_manager

        addon_path = get_addon_dir()
        
        append_from_blendfile = bpy.data.filepath

        tools = os.path.join(addon_path, "resources", "tools", "open_selected.py")
        open_blend_file = os.path.join(addon_path, "resources", "empty_file.blend")

        selected_objects = ""
        for ob in context.selected_objects:
            if ob.type == "MESH":
                selected_objects += ob.name + "|"

        selected_objects = selected_objects[:-1] # remove last character

        sub = subprocess.Popen(
            [
                bpy.app.binary_path,   # path to blender.exe
                open_blend_file,       # open file
                "--python",
                tools,                 # path to python script
                append_from_blendfile, # from blendfile append collection
                "Object",
                selected_objects       # selected objects A|B|C|D etc
            ]
        )

        return {"FINISHED"}



# class VIEW3D_OT_AddFolder(Operator):
#     """Create new folder"""
#     bl_idname = "view3d.add_folder"
#     bl_label = "Add Folder?"

#     folder_place: StringProperty()
#     name_new_folder: StringProperty(
#         name="Name New Folder",
#         default=""
#     )

#     def draw(self, context):
#         layout = self.layout
#         row = layout.row()
#         row.label(text="Name New Folder")
#         row.prop(self, "name_new_folder", text="")

#     def invoke(self, context, event):
#         return context.window_manager.invoke_props_dialog(self)

#     def execute(self, context):
#         nexus_model_SCN = context.scene.nexus_model_manager

#         addon_prefs = get_addon_prefs()
#         library_dir = addon_prefs.library_list
#         library_name = None
#         category_name = None

#         if self.folder_place == "LIBRARY": # create library folder
#             library_name = self.name_new_folder
#             new_folder_path = os.path.join(library_dir, library_name)
#             if os.path.exists(new_folder_path):
#                 self.report({"ERROR"}, "Folder already exists!")
#             else:
#                 os.makedirs(new_folder_path)
#                 # nexus_model_SCN.library_list = library_name # move to new folder
#                 self.report({"INFO"}, "Folder created: {}".format(new_folder_path))

#         elif self.folder_place == "CATEGORY": # create category folder
#             library_name = nexus_model_SCN.library_list
#             category_name = self.name_new_folder
#             new_folder_path = os.path.join(library_dir, library_name, category_name)
#             if os.path.exists(new_folder_path):
#                 self.report({"ERROR"}, "Folder already exists!")
#             else:
#                 os.makedirs(new_folder_path)
#                 # nexus_model_SCN.category_list = library_name # move to new folder
#                 self.report({"INFO"}, "Folder created: {}".format(new_folder_path))

#         self.name_new_folder = "" # clear string
#         return {"FINISHED"}