bl_info = {
	"name": "Nexus Model Manager",
	"author": "Nexus Studio",
	"version": (0, 8, 2),
	"blender": (2, 79, 0),
	"location": "View 3D > Tool Shelf",
	"description": "Tools",
	"warning": "",
	"wiki_url": "https://github.com/Hichigo/NexusModelManager",
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

############################ Furniture ##########################
def make_furniture_category(self, context):
	path_models = context.window_manager.models_dir

	return make_models_category(path_models, "Furniture")

##################################################################
############################ Previews ############################
##################################################################


######### Furniture Previews ##########

def enum_previews_furniture_items(self, context):
	""" create furniture items prewiews """
	enum_items = []

	category = bpy.data.window_managers['WinMan'].furniture_category
	path_models = bpy.data.window_managers['WinMan'].models_dir
	directory = os.path.join(path_models, "Furniture", category, "renders")
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

###########################################################################
############################ Addon preferences ############################
###########################################################################

class Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	path_to_library = bpy.types.Scene.path_to_library = StringProperty(
		name="Path",
		default=os.path.join(os.path.dirname(__file__), "Models"),
		description="The path to your library",
		subtype="DIR_PATH",
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

	@classmethod
	def poll(cls, context):
		return context.object.mode == 'OBJECT'

	def draw(self, context):
		furniture_prev = bpy.data.window_managers["WinMan"].furniture_previews
		layout = self.layout
		wm = context.window_manager


############## Furniture Panel ##############

		col = layout.column()
		col.prop(wm, "models_dir")
		col.prop(wm, "link_model")

		box = layout.box()
		box.label(text="FURNITURE")
####### Drop Down Menu
		row = box.row()
		row.prop(wm, "furniture_category", text="")
####### Previews
		row = box.row()
		row.scale_y = 1.5
		row.template_icon_view(wm, "furniture_previews", show_labels=True)
####### Model Name
		row = box.row()
		row.alignment = 'CENTER'
		row.scale_y = 0.5
		row.label(os.path.splitext(furniture_prev)[0])
####### Add Button
		row = box.row()
		row.operator("add.furniture", icon="ZOOMIN", text="Add Furniture Model")


		############## Library Panel ##############


		box = layout.box()
		box.label(text="Library Folder:")
		row = box.row()
		row.operator("library.path", icon="ZOOMIN", text="Open Library Folder")


################################################################
############################ Append ############################
################################################################

####### Append Furniture #######


class OBJECT_OT_AddButton(bpy.types.Operator):
	bl_idname = "add.furniture"
	bl_label = "Add Furniture"

	def execute(self, context):
		
		scn = context.scene
		selected_preview = bpy.data.window_managers["WinMan"].furniture_previews
		category = bpy.data.window_managers["WinMan"].furniture_category
		path_models = bpy.data.window_managers["WinMan"].models_dir
		is_link = bpy.data.window_managers["WinMan"].link_model

		filename = os.path.splitext(selected_preview)[0]
		filepath = os.path.join(path_models, "Furniture", category, filename + ".blend")
		filepath_group = filepath + "\\Group\\"
		
		bpy.ops.object.select_all(action='DESELECT')

		if is_link:
			with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
				data_to.groups = data_from.groups

			for group in data_to.groups:
				ob = bpy.data.objects.new(group.name, None)
				ob.dupli_group = group
				ob.dupli_type = 'GROUP'
				scn.objects.link(ob)
		else:
			# with bpy.data.libraries.load(filepath) as (data_from, data_to):
			# 	data_to.groups = [selected_preview]

			# for group in data_to.groups:
			filepath_group_name = filepath_group + filename
			print("TRRRRRRRYAU", filepath_group)
			print("TRRRRRRRYAU", filename)
			print("TRRRRRRRYAU", filepath_group_name)
			bpy.ops.wm.append(filepath=filepath_group_name, filename=filename, directory=filepath_group)


		return{'FINISHED'}

######################################################################
############################ Library path ############################
######################################################################

class Lib_Path(bpy.types.Operator):

	bl_idname = "library.path"
	bl_label = "Library Path"
	
	def execute(self, context):
		filepath = context.window_manager.models_dir
		bpy.ops.wm.path_open(filepath=filepath)
		return {'FINISHED'}


######################################################################
############################## Register ##############################
######################################################################

def register():

	bpy.utils.register_class(Preferences)
	bpy.utils.register_class(Lib_Path)
	bpy.utils.register_module(__name__)

	user_preferences = bpy.context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences

	WindowManager.models_dir = StringProperty(
		name="Folder Path",
		subtype="DIR_PATH",
		default=addon_prefs.path_to_library
		)

	WindowManager.link_model = BoolProperty(
		name="Link",
		description="If True link model else append model",
		default=False
		)

# Furniture
	WindowManager.furniture_previews = EnumProperty(
		items=enum_previews_furniture_items,
		)

	WindowManager.furniture_category = EnumProperty(
		items=make_furniture_category,
		)

	pcoll = bpy.utils.previews.new()
	pcoll.furniture_previews_dir = ""
	pcoll.furniture_previews = ()

	furniture_collections["main"] = pcoll


######################################################################
############################# Unregister #############################
######################################################################

def unregister():

	bpy.utils.unregister_class(Preferences)
	bpy.utils.unregister_class(Lib_Path)

	del WindowManager.furniture_previews
	del WindowManager.furniture_category

	for pcoll in furniture_collections.values():
		bpy.utils.previews.remove(pcoll)
	furniture_collections.clear()

	bpy.utils.unregister_module(__name__)
	del WindowManager.models_dir
	del WindowManager.link_model




if __name__ == "__main__":
	register()
