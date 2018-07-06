bl_info = {
	"name": "Nexus Model Manager",
	"author": "Nexus Studio",
	"version": (0, 0, 1),
	"blender": (2, 79, 0),
	"location": "View 3D > Tool Shelf",
	"description": "Tools",
	"warning": "",
	"wiki_url": "None",
	"category": "Add Mesh"
	}

import bpy
import os
from bpy.props import *
import bpy.utils.previews
from bpy.types import WindowManager



###########################################################################
#################### function dinamicaly make category ####################
###########################################################################
def get_path_to_library():
	user_preferences = bpy.context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences
	path = addon_prefs.path_to_library

	return path

def make_models_category(folder):
	path_to_library = get_path_to_library()
	print(path_to_library)

	category_folder_path = os.path.join(path_to_library, folder)
	print(category_folder_path)
	dirs = os.listdir(category_folder_path)
	i = 0
	mode_options = []

	for dir in dirs:
		item = (dir, dir, '', i)
		mode_options.append(item)
		i += 1

	return mode_options





###########################################################################
############################ Addon preferences ############################
###########################################################################

class Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	path_to_library = bpy.types.Scene.path_to_library = StringProperty(
		name="Path",
		default="C://Users/ivan/AppData/Roaming/Blender Foundation/Blender/2.79/scripts/addons/Chocofur_Model_Manager/Models",
		description="The path to your library",
		subtype="FILE_PATH",
	)

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		col.prop(self, "path_to_library")





#################################################################
############################ Toolbar ############################
#################################################################


class PreviewsPanel(bpy.types.Panel):

	bl_label = "Nexus Model Manager"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Nexus Model Manager"

	def draw(self, context):
		# furniture_prev = bpy.data.window_managers["WinMan"].furniture_previews
		# accessorie_prev = bpy.data.window_managers["WinMan"].accessorie_previews
		# detail_prev = bpy.data.window_managers["WinMan"].detail_previews
		layout = self.layout
		wm = context.window_manager


############## Furniture Panel ##############
		
		row = layout.row()
		row.prop(wm, "my_previews_dir")

		box = layout.box()
		box.label(text="FURNITURE")
####### Drop Down Menu
		# row = box.row()
		# row.prop(context.scene.furniture, "furniture_category", text="")
####### Previews
		# row = box.row()
		# row.scale_y = 1.5
		# row.template_icon_view(context.window_manager, "furniture_previews", show_labels=True)
####### Model Name
		# row = box.row()
		# row.alignment = 'CENTER'
		# row.scale_y = 0.5
		# row.label(furniture_prev.split('.jpg')[0])
####### Add Button
		# row = box.row()
		# row.operator("add.furniture", icon="ZOOMIN", text="Add Furniture Model")



		############## Library Panel ##############


		box = layout.box()
		box.label(text="Library Folder:")
		row = box.row()
		row.operator("library.path", icon="ZOOMIN", text="Open Library Folder")



class Lib_Path(bpy.types.Operator):

	bl_idname = "library.path"
	bl_label = "Library Path"
	
	def execute(self, context):
		filepath = context.window_manager.my_previews_dir
		bpy.ops.wm.path_open(filepath=filepath)
		return {'FINISHED'}

def register():

	bpy.utils.register_class(Preferences)
	bpy.utils.register_class(Lib_Path)
	bpy.utils.register_class(PreviewsPanel)

	user_preferences = bpy.context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences

	WindowManager.my_previews_dir = StringProperty(
		name="Folder Path",
		subtype='DIR_PATH',
		default=addon_prefs.path_to_library
		)

	# WindowManager.my_previews = EnumProperty(
	# 	items=enum_previews_from_directory_items,
	# 	)


def unregister():

	bpy.utils.unregister_class(Preferences)
	bpy.utils.unregister_class(Lib_Path)
	bpy.utils.unregister_class(PreviewsPanel)

	del WindowManager.my_previews
	del bpy.types.Scene.path_to_library


if __name__ == "__main__":
	register()