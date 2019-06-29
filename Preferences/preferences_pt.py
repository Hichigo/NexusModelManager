import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import *

import os

from .. enum_preview_utils import make_library_list_folders
from .. functions import get_addon_dir

class ListFolder(PropertyGroup):
	path_to_folder: StringProperty(name="Path to folder library", default="", subtype="DIR_PATH")

class Preferences(AddonPreferences):
	bl_idname = __name__.split(".")[0]
	
	library_folders: CollectionProperty(name="Library Folders", type=ListFolder)

	library_list: EnumProperty(
		name="Current Library",
		items=make_library_list_folders
	)

	path_to_library: StringProperty(
		name="Library Path",
		default=os.path.join(get_addon_dir(), "resources", "LibraryModels"),
		description="The path to your library",
		subtype="DIR_PATH"
	)

	path_to_render_scenes: StringProperty(
		name="Render Scene Path",
		default=os.path.join(get_addon_dir(), "resources", "render_scenes"),
		description="The path to your render scenes",
		subtype="DIR_PATH"
	)

	preview_asset_scale: FloatProperty(
		name="Asset Image Scale",
		description="Preview assets image scale",
		min=1,
		max=100,
		default=7
	)

	def draw(self, context):
		layout = self.layout
		wm = context.window_manager

		col = layout.column(align=True)

		row = col.row()
		row.prop(self, "library_list")
		row.operator("wm.remove_library_folder", icon="REMOVE", text="")

		col.prop(self, "path_to_render_scenes")
		col.prop(self, "preview_asset_scale")
		

		box = layout.box()
		box.label(text="Create new library item")
		row = box.row()
		row.prop(wm, "new_library_path")
		row.operator("wm.add_library_folder", icon="ADD", text="")