bl_info = {
	"name": "Nexus Model Manager",
	"author": "Nexus Studio",
	"version": (1, 1, 1),
	"blender": (2, 80, 0),
	"location": "View 3D > 'N' menu",
	"description": "Tools",
	"warning": "",
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
from .MeshPaint.random_list_ui import *

from .Preferences.preferences_pt import *
from .Preferences.preferences_op import *

from .properties import *

from .functions import get_addon_prefs

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

		addon_prefs = get_addon_prefs()
		library_dir = addon_prefs.library_list

		############## Library folder button ##############
		box = layout.box()
		box.label(text="Library Folder:")
		col = box.column(align=True)
		col.prop(addon_prefs, "library_list")
		col.operator("view3d.library_path", icon="FILE_FOLDER", text="Open Library Folder")

############################ Library path ############################
class VIEW3D_OT_LibraryPath(Operator):
	"""Open folder library"""
	bl_idname = "view3d.library_path"
	bl_label = "Library Path"
	
	def execute(self, context):
		addon_prefs = get_addon_prefs()
		library_dir = addon_prefs.library_list
		if os.path.isdir(library_dir):
			bpy.ops.wm.path_open(filepath=library_dir)
		else:
			self.report({"ERROR"}, "Folder not exists!")
		return {"FINISHED"}

############################## Register ##############################
classes = (
	ListItem,
	ListFolder,
	STRING_UL_RandomAssets,
	VIEW3D_PT_MainPanel,
	VIEW3D_PT_CreateAsset,
	VIEW3D_PT_ManagerPreviews,
	VIEW3D_PT_MeshPaint,
	Preferences,
	VIEW3D_OT_LibraryPath,
	VIEW3D_OT_AssetPath,
	VIEW3D_OT_CreateAsset,
	VIEW3D_OT_SetNewLibrary,
	VIEW3D_OT_SetNewCategory,
	VIEW3D_OT_OpenInNewFile,
	VIEW3D_OT_ImagePath,
	SCENE_OT_AddListItem,
	SCENE_OT_RemoveListItem,
	NexusModelManager_WM_Properties,
	UIList_WM_Properties,
	VIEW3D_OT_MeshPaint,
	VIEW3D_OT_AddModel,
	# VIEW3D_OT_AddFolder,
	WM_OT_AddLibraryFolder,
	WM_OT_RemoveLibraryFolder,
	VIEW3D_OT_SearchAsset
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	addon_prefs = get_addon_prefs()

	WindowManager.new_library_path = StringProperty(
		name="New Library Path",
		subtype="DIR_PATH",
		default=""
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

############################# Unregister #############################
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