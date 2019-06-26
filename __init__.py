bl_info = {
	"name": "Nexus Model Manager",
	"author": "Nexus Studio",
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
	"location": "View 3D > 'N' menu",
	"description": "Tools",
	"warning": "BETA",
	"wiki_url": "https://github.com/Hichigo/NexusModelManager",
	"category": "Object"
}

import bpy
import os

from bpy.props import *
import bpy.utils.previews
from bpy.types import AddonPreferences, WindowManager, Panel, Operator

from .CreateAsset.create_asset_op import *
from .CreateAsset.create_asset_pt import *

from .PreviewAssets.preview_assets_op import *
from .PreviewAssets.preview_assets_pt import *

from .MeshPaint.mesh_paint_op import *
from .MeshPaint.mesh_paint_pt import *

from .properties import *

from .random_list_ui import *

from .functions import get_addon_prefs

###########################################################################
############################ Addon preferences ############################
###########################################################################

class Preferences(AddonPreferences):
	bl_idname = __name__

	path_to_library: StringProperty(
		name="Library Path",
		default=os.path.join(os.path.dirname(__file__), "LibraryModels"),
		description="The path to your library",
		subtype="DIR_PATH"
	)

	path_to_render_scenes: StringProperty(
		name="Render Scene Path",
		default=os.path.join(os.path.dirname(__file__), "resources", "render_scenes"),
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

		col = layout.column(align=True)
		col.prop(self, "path_to_library")
		col.prop(self, "path_to_render_scenes")
		col.prop(self, "preview_asset_scale")

#################################################################
############################ Toolbar ############################
#################################################################
class VIEW3D_PT_MainPanel(Panel):
	bl_label = "Nexus Model Manager"
	bl_idname = "VIEW3D_PT_MainPanel"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Nexus"

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def draw(self, context):
		layout = self.layout
		wm = context.window_manager

		############## Library folder button ##############
		box = layout.box()
		box.label(text="Library Folder:")
		col = box.column(align=True)
		col.prop(wm, "nexus_model_manager_dir_resource")
		col.operator("view3d.library_path", icon="FILE_FOLDER", text="Open Library Folder")

################################################################
############################ Append ############################
################################################################

# class VIEW3D_OT_RemoveFolder(bpy.types.Operator):
# 	"""Remove Folder"""
# 	bl_idname = "view3d.remove_folder"
# 	bl_label = "Do you really want to delete the folder and everything inside?"
# 	bl_options = {'REGISTER', 'INTERNAL'}

# 	folder_place: StringProperty()

# 	def invoke(self, context, event):
# 		return context.window_manager.invoke_confirm(self, event)

# 	def execute(self, context):
# 		import shutil

# 		nexus_model_SCN = context.scene.nexus_model_manager
		
# 		library_dir = context.window_manager.nexus_model_manager_dir_resource
# 		library_name = nexus_model_SCN.library_list
# 		category_name = nexus_model_SCN.category_list
# 		remove_folder_path = os.path.join(library_dir, library_name)

# 		if self.folder_place == "LIBRARY":
# 			shutil.rmtree(remove_folder_path)
# 		elif self.folder_place == "CATEGORY":
# 			remove_folder_path = os.path.join(remove_folder_path, category_name)
# 			shutil.rmtree(remove_folder_path)
# 		else:
# 			self.report({"INFO"}, "Something went wrong!")
# 			return {'FINISHED'}

# 		self.report({"INFO"}, "Folder removed: {}".format(remove_folder_path))

# 		return {'FINISHED'}

######################################################################
############################ Library path ############################
######################################################################

class VIEW3D_OT_LibraryPath(Operator):
	"""Open folder library"""
	bl_idname = "view3d.library_path"
	bl_label = "Library Path"
	
	def execute(self, context):
		library_dir = context.window_manager.nexus_model_manager_dir_resource
		bpy.ops.wm.path_open(filepath=library_dir)
		return {"FINISHED"}

######################################################################
############################## Register ##############################
######################################################################

classes = (
	ListItem,
	STRING_UL_RandomAssets,
	VIEW3D_PT_MainPanel,
	VIEW3D_PT_CreateAsset,
	VIEW3D_PT_ManagerPreviews,
	VIEW3D_PT_MeshPaint,
	Preferences,
	VIEW3D_OT_LibraryPath,
	VIEW3D_OT_AssetPath,
	VIEW3D_OT_CreateAsset,
	VIEW3D_OT_ImagePath,
	SCENE_OT_AddListItem,
	SCENE_OT_RemoveListItem,
	NexusModelManager_WM_Properties,
	UIList_WM_Properties,
	VIEW3D_OT_MeshPaint,
	VIEW3D_OT_AddModel,
	VIEW3D_OT_AddFolder,
	# VIEW3D_OT_RemoveFolder,
	VIEW3D_OT_SearchAsset
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	addon_prefs = get_addon_prefs()

	WindowManager.nexus_model_manager_dir_resource = StringProperty(
		name="Library Directory",
		subtype="DIR_PATH",
		default=addon_prefs.path_to_library
	)

	pcoll = bpy.utils.previews.new()
	pcoll.asset_previews_dir = ""
	pcoll.asset_previews = ()
	asset_collections["main"] = pcoll

	pcoll = bpy.utils.previews.new()
	pcoll.render_scene_previews_dir = ""
	pcoll.asset_previews = ()
	render_scene_collections["main"] = pcoll

	bpy.types.Scene.nexus_model_manager = bpy.props.PointerProperty(type=NexusModelManager_WM_Properties)
	bpy.types.Scene.random_asset_list = bpy.props.PointerProperty(type=UIList_WM_Properties)


######################################################################
############################# Unregister #############################
######################################################################

def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)

	for pcoll in asset_collections.values():
		bpy.utils.previews.remove(pcoll)
	asset_collections.clear()

	for pcoll in render_scene_collections.values():
		bpy.utils.previews.remove(pcoll)
	render_scene_collections.clear()

	del bpy.types.Scene.nexus_model_manager
	del bpy.types.Scene.random_asset_list

if __name__ == "__main__":
	register()