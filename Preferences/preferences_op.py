import bpy
from bpy.types import Operator
from bpy.props import *

from .. functions import get_addon_prefs

class WM_OT_AddLibraryFolder(Operator):
	"""Add library folder"""
	bl_idname = "wm.add_library_folder"
	bl_label = "Enter library name"
	
	name_new_library: StringProperty(
		name="Name New Library",
		default=""
	)

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.prop(self, "name_new_library")

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		wm = context.window_manager
		addon_prefs = get_addon_prefs()
		new_index = len(addon_prefs.library_folders)
		addon_prefs.library_folders.add()

		addon_prefs.library_folders[new_index].name = self.name_new_library
		addon_prefs.library_folders[new_index].path_to_folder = wm.new_library_path

		self.name_new_library = ""
		
		return {"FINISHED"}

class WM_OT_RemoveLibraryFolder(Operator):
	"""Remove library folder"""
	bl_idname = "wm.remove_library_folder"
	bl_label = "Remove library folder"

	def execute(self, context):
		addon_prefs = get_addon_prefs()
		library_dir = addon_prefs.library_list

		for i, folder in enumerate(addon_prefs.library_folders):
			if folder.path_to_folder == library_dir:
				addon_prefs.library_folders.remove(i)

		return {"FINISHED"}