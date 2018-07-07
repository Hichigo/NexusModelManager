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

def make_models_category(path, folder):

	category_folder_path = os.path.join(path, folder)
	dirs = os.listdir(category_folder_path)
	i = 0
	mode_options = []

	for dir in dirs:
		item = (dir, dir, '', i)
		mode_options.append(item)
		i += 1

	return mode_options

##################################################################
############################ Previews ############################
##################################################################

####### Furniture Previews #######


def enum_previews_furniture_items(self, context):
	""" create furniture items prewiews """
	enum_items = []

	category = context.scene.furniture.furniture_category
	path_models = bpy.data.window_managers['WinMan'].my_previews_dir
	print(path_models)
	print(category)
	directory = os.path.join(path_models, "Furniture", category, "Renders")
	print(directory)
	image_extensions = (".jpg", ".JPG", ".png", ".jpeg")

	if context is None:
		return enum_items

	wm = context.window_manager

	pcoll = furniture_collections["main"]

	if directory == pcoll.furniture_previews_dir:
		return pcoll.furniture_previews

	if directory and os.path.exists(directory):
		image_paths = []
		for fn in os.listdir(directory):
			if fn.lower().endswith(image_extensions):
				image_paths.append(fn)

		for i, name in enumerate(image_paths):
			filepath = os.path.join(directory, name)
			
			if filepath in pcoll:
				enum_items.append((name, name, "", pcoll[filepath].icon_id, i))
			else:
				thumb = pcoll.load(filepath, filepath, 'IMAGE')
				enum_items.append((name, name, "", thumb.icon_id, i))
	enum_items.sort()

	pcoll.furniture_previews = enum_items
	pcoll.furniture_previews_dir = directory
	return pcoll.furniture_previews

furniture_collections = {}


class Furniture_Category(bpy.types.PropertyGroup):
	path_models = bpy.data.window_managers['WinMan'].my_previews_dir

	mode_options = make_models_category(path_models, 'Furniture')

	furniture_category = bpy.props.EnumProperty(
		name="furniture_category",
		items=mode_options,
		description="Select Furniture",
		default=mode_options[0]
	)


###########################################################################
############################ Addon preferences ############################
###########################################################################

class Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	path_to_library = bpy.types.Scene.path_to_library = StringProperty(
		name="Path",
		default="E:\\Projects\\Blender\\Models",
		description="The path to your library",
		subtype="FILE_PATH",
	)
	print("olololol ya voditel NLO!")

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
		furniture_prev = bpy.data.window_managers["WinMan"].furniture_previews
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
		row = box.row()
		row.prop(context.scene.furniture, "furniture_category", text="")
####### Previews
		row = box.row()
		row.scale_y = 1.5
		row.template_icon_view(context.window_manager, "furniture_previews", show_labels=True)
####### Model Name
		row = box.row()
		row.alignment = 'CENTER'
		row.scale_y = 0.5
		row.label(furniture_prev.split('.jpg')[0])
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
	

	user_preferences = bpy.context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences

	WindowManager.my_previews_dir = StringProperty(
		name="Folder Path",
		subtype='DIR_PATH',
		default=addon_prefs.path_to_library
		)

	WindowManager.furniture_previews = EnumProperty(
		items=enum_previews_furniture_items, # TODO: create function
		)
	pcoll = bpy.utils.previews.new()
	pcoll.furniture_previews_dir = ""
	pcoll.furniture_previews = ()

	furniture_collections["main"] = pcoll

	bpy.utils.register_class(Furniture_Category)
	bpy.utils.register_class(Lib_Path)
	bpy.utils.register_class(PreviewsPanel)
	bpy.utils.register_module(__name__)

	bpy.types.Scene.furniture = bpy.props.PointerProperty(type=Furniture_Category)




def unregister():

	bpy.utils.unregister_class(Preferences)
	bpy.utils.unregister_class(Furniture_Category)
	bpy.utils.unregister_class(Lib_Path)
	bpy.utils.unregister_class(PreviewsPanel)

	del WindowManager.furniture_previews

	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()


	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.path_to_library
	del bpy.types.Scene.furniture


if __name__ == "__main__":
	register()