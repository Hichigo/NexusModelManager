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

def make_list_folder(path):

	dirs = os.listdir(path)
	i = 0
	mode_options = []

	for dir in dirs:
		if os.path.isdir(os.path.join(path, dir)):
			item = (dir, dir, '', i)
			mode_options.append(item)
			i += 1

	return mode_options

############################ Category ##########################
def make_category_list(self, context):
	path_library = context.window_manager.models_dir
	library = context.window_manager.library_list
	path_category = os.path.join(path_library, library)

	return make_list_folder(path_category)

############################ Library ##########################
def make_library_list(self, context):
	path_library = context.window_manager.models_dir

	return make_list_folder(path_library)

##################################################################
############################ Previews ############################
##################################################################


######### Assets Previews ##########

def enum_previews_asset_items(self, context):
	""" create assets items prewiews """
	enum_items = []

	category = bpy.data.window_managers['WinMan'].category_list
	path_models = bpy.data.window_managers['WinMan'].models_dir
	library = bpy.data.window_managers["WinMan"].library_list
	directory = os.path.join(path_models, library, category)


	if context is None:
		return enum_items

	wm = context.window_manager

	pcoll = asset_collections["main"]

	if directory == pcoll.asset_previews_dir:
		return pcoll.asset_previews

	if directory and os.path.exists(directory):
		assets_names = []
		for fn in os.listdir(directory):
			assets_names.append(fn)

		for i, name in enumerate(assets_names):
			filepath = os.path.join(directory, name, "render", name + ".png")

			if filepath in pcoll:
				enum_items.append((name, name, "", pcoll[filepath].icon_id, i))
			else:
				thumb = pcoll.load(filepath, filepath, 'IMAGE')
				enum_items.append((name, name, "", thumb.icon_id, i))
	enum_items.sort()

	pcoll.asset_previews = enum_items
	pcoll.asset_previews_dir = directory
	return pcoll.asset_previews

asset_collections = {}

###########################################################################
############################ Addon preferences ############################
###########################################################################

class Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	path_to_library = bpy.types.Scene.path_to_library = StringProperty(
		name="Path",
		default=os.path.join(os.path.dirname(__file__), "LibraryModels"),
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
		furniture_prev = bpy.data.window_managers["WinMan"].asset_previews
		layout = self.layout
		wm = context.window_manager


############## Furniture Panel ##############

		col = layout.column()
		col.prop(wm, "models_dir")
		col.prop(wm, "link_model")

		box = layout.box()
		box.label(text="Manager")

####### Drop Down Menu library
		row = box.row()
		row.label(text="Library")
		row.prop(wm, "library_list", text="")

####### Drop Down Menu category
		row = box.row()
		row.label(text="Category")
		row.prop(wm, "category_list", text="")

####### Previews
		row = box.row()
		row.scale_y = 1.5
		row.template_icon_view(wm, "asset_previews", show_labels=True)

####### Model Name
		row = box.row()
		row.alignment = 'CENTER'
		row.scale_y = 0.5
		row.label(os.path.splitext(furniture_prev)[0])

####### Add Button
		row = box.row()
		row.operator("add.furniture", icon="ZOOMIN", text="Add Model")


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
		selected_preview = bpy.data.window_managers["WinMan"].asset_previews
		category = bpy.data.window_managers["WinMan"].category_list
		library = bpy.data.window_managers["WinMan"].library_list
		path_models = bpy.data.window_managers["WinMan"].models_dir
		is_link = bpy.data.window_managers["WinMan"].link_model

		filename = os.path.splitext(selected_preview)[0]
		filepath = os.path.join(path_models, library, category, filename, filename + ".blend")
		filepath_group = os.path.join(filepath, "Group")

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
			filepath_group_name = filepath_group + filename
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

	WindowManager.asset_previews = EnumProperty(
		items=enum_previews_asset_items,
		)

	WindowManager.library_list = EnumProperty(
		items=make_library_list,
		)

	WindowManager.category_list = EnumProperty(
		items=make_category_list,
		)

	pcoll = bpy.utils.previews.new()
	pcoll.asset_previews_dir = ""
	pcoll.asset_previews = ()

	asset_collections["main"] = pcoll


######################################################################
############################# Unregister #############################
######################################################################

def unregister():

	bpy.utils.unregister_class(Preferences)
	bpy.utils.unregister_class(Lib_Path)

	del WindowManager.asset_previews
	del WindowManager.category_list

	for pcoll in asset_collections.values():
		bpy.utils.previews.remove(pcoll)
	asset_collections.clear()

	bpy.utils.unregister_module(__name__)
	del WindowManager.models_dir
	del WindowManager.library_list
	del WindowManager.link_model




if __name__ == "__main__":
	register()
