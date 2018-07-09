bl_info = {
	"name": "Nexus Model Manager",
	"author": "Nexus Studio",
	"version": (0, 8, 1),
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
	path_models = bpy.context.window_manager.models_dir

	return make_models_category(path_models, "Furniture")

############################ Detail ############################
def make_detail_category(self, context):
	path_models = bpy.context.window_manager.models_dir

	return make_models_category(path_models, "Detail")

########################## Accessorie ##########################
def make_accessorie_category(self, context):
	path_models = bpy.context.window_manager.models_dir

	return make_models_category(path_models, "Accessorie")

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

def enum_previews_accessorie_items(self, context):
	""" create accessorie items prewiews """
	enum_items = []

	category = bpy.data.window_managers['WinMan'].accessorie_category
	path_models = bpy.data.window_managers['WinMan'].models_dir
	directory = os.path.join(path_models, "Accessorie", category, "renders")
	image_extensions = (".jpg", ".JPG", ".png", ".jpeg")

	if context is None:
		return enum_items

	wm = context.window_manager

	pcoll = accessorie_collections["main"]

	if directory == pcoll.accessorie_previews_dir:
		return pcoll.accessorie_previews

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

	pcoll.accessorie_previews = enum_items
	pcoll.accessorie_previews_dir = directory
	return pcoll.accessorie_previews

accessorie_collections = {}

def enum_previews_detail_items(self, context):
	""" create detail items prewiews """
	enum_items = []

	category = bpy.data.window_managers['WinMan'].detail_category
	path_models = bpy.data.window_managers['WinMan'].models_dir
	directory = os.path.join(path_models, "Detail", category, "renders")
	image_extensions = (".jpg", ".JPG", ".png", ".jpeg")

	if context is None:
		return enum_items

	wm = context.window_manager

	pcoll = detail_collections["main"]

	if directory == pcoll.detail_previews_dir:
		return pcoll.detail_previews

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

	pcoll.detail_previews = enum_items
	pcoll.detail_previews_dir = directory
	return pcoll.detail_previews

detail_collections = {}

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

	def draw(self, context):
		furniture_prev = bpy.data.window_managers["WinMan"].furniture_previews
		accessorie_prev = bpy.data.window_managers["WinMan"].accessorie_previews
		detail_prev = bpy.data.window_managers["WinMan"].detail_previews
		layout = self.layout
		wm = context.window_manager


############## Furniture Panel ##############

		col = layout.column()
		col.prop(wm, "models_dir")

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
		row.label(furniture_prev.split('.jpg')[0])
####### Add Button
		row = box.row()
		row.operator("add.furniture", icon="ZOOMIN", text="Add Furniture Model")

############## Accessorie Panel ##############

		box = layout.box()
		box.label(text="ACCESSORIE")
####### Drop Down Menu
		row = box.row()
		row.prop(wm, "accessorie_category", text="")
####### Previews
		row = box.row()
		row.scale_y = 1.5
		row.template_icon_view(wm, "accessorie_previews", show_labels=True)
####### Model Name
		row = box.row()
		row.alignment = 'CENTER'
		row.scale_y = 0.5
		row.label(accessorie_prev.split('.jpg')[0])
####### Add Button
		row = box.row()
		row.operator("add.accessorie", icon="ZOOMIN", text="Add Accessorie Model")

############## Detail Panel ##############

		box = layout.box()
		box.label(text="DETAIL")
####### Drop Down Menu
		row = box.row()
		row.prop(wm, "detail_category", text="")
####### Previews
		row = box.row()
		row.scale_y = 1.5
		row.template_icon_view(wm, "detail_previews", show_labels=True)
####### Model Name
		row = box.row()
		row.alignment = 'CENTER'
		row.scale_y = 0.5
		row.label(detail_prev.split('.jpg')[0])
####### Add Button
		row = box.row()
		row.operator("add.detail", icon="ZOOMIN", text="Add Detail Model")


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
		selected_preview = bpy.data.window_managers["WinMan"].furniture_previews
		category = bpy.data.window_managers['WinMan'].furniture_category
		path_models = bpy.data.window_managers['WinMan'].models_dir
		scn = bpy.context.scene
		filepath = os.path.join(path_models, "Furniture", category, os.path.splitext(selected_preview)[0], ".blend")
		
		bpy.ops.object.select_all(action='DESELECT')
		
		with bpy.data.libraries.load(filepath) as (data_from, data_to):
			object_list = [obj for obj in data_from.objects]
			data_to.objects = data_from.objects
			if data_from.groups:
				data_to.groups = data_from.groups

		for obj in bpy.data.objects:
			for data in object_list:
				if obj.name.startswith(data) and obj.name not in bpy.context.scene.objects:
					idx = object_list.index(data)
					scn.objects.link(obj)
					obj.select = True

		return{'FINISHED'}

####### Append Accessorie ####### 


class OBJECT_OT_AddButton(bpy.types.Operator):
	bl_idname = "add.accessorie"
	bl_label = "Add Accessorie"

	def execute(self, context):
		selected_preview = bpy.data.window_managers["WinMan"].accessorie_previews
		category = bpy.data.window_managers['WinMan'].accessorie_category
		path_models = bpy.data.window_managers['WinMan'].models_dir
		scn = bpy.context.scene
		filepath = os.path.join(path_models, "Accessorie", category, os.path.splitext(selected_preview)[0], ".blend")
		
		bpy.ops.object.select_all(action='DESELECT')
		
		with bpy.data.libraries.load(filepath) as (data_from, data_to):
			object_list = [obj for obj in data_from.objects]
			data_to.objects = data_from.objects
			if data_from.groups:
				data_to.groups = data_from.groups

		for obj in bpy.data.objects:
			for data in object_list:
				if obj.name.startswith(data) and obj.name not in bpy.context.scene.objects:
					idx = object_list.index(data)
					scn.objects.link(obj)
					obj.select = True

		return{'FINISHED'}

####### Append Detail ####### 


class OBJECT_OT_AddButton(bpy.types.Operator):
	bl_idname = "add.detail"
	bl_label = "Add Detail"

	def execute(self, context):
		selected_preview = bpy.data.window_managers["WinMan"].detail_previews
		category = bpy.data.window_managers['WinMan'].detail_category
		path_models = bpy.data.window_managers['WinMan'].models_dir
		scn = bpy.context.scene
		filepath = os.path.join(path_models, "Detail", category, os.path.splitext(selected_preview)[0], ".blend")
		
		bpy.ops.object.select_all(action='DESELECT')
		
		with bpy.data.libraries.load(filepath) as (data_from, data_to):
			object_list = [obj for obj in data_from.objects]
			data_to.objects = data_from.objects
			if data_from.groups:
				data_to.groups = data_from.groups

		for obj in bpy.data.objects:
			for data in object_list:
				if obj.name.startswith(data) and obj.name not in bpy.context.scene.objects:
					idx = object_list.index(data)
					scn.objects.link(obj)
					obj.select = True

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



def register():

	bpy.utils.register_class(Preferences)
	bpy.utils.register_class(Lib_Path)
	bpy.utils.register_module(__name__)

	user_preferences = bpy.context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences

	WindowManager.models_dir = StringProperty(
		name="Folder Path",
		subtype='DIR_PATH',
		default=addon_prefs.path_to_library
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

# Accessorie
	WindowManager.accessorie_previews = EnumProperty(
		items=enum_previews_accessorie_items,
		)

	WindowManager.accessorie_category = EnumProperty(
		items=make_accessorie_category,
		)

	pcoll = bpy.utils.previews.new()
	pcoll.accessorie_previews_dir = ""
	pcoll.accessorie_previews = ()

	accessorie_collections["main"] = pcoll

# Detail
	WindowManager.detail_previews = EnumProperty(
		items=enum_previews_detail_items,
		)

	WindowManager.detail_category = EnumProperty(
		items=make_detail_category,
		)

	pcoll = bpy.utils.previews.new()
	pcoll.detail_previews_dir = ""
	pcoll.detail_previews = ()

	detail_collections["main"] = pcoll




def unregister():

	bpy.utils.unregister_class(Preferences)
	bpy.utils.unregister_class(Lib_Path)

	del WindowManager.furniture_previews

	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()

	del WindowManager.accessorie_previews

	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()

	del WindowManager.detail_previews

	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()

	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.path_to_library
	del bpy.types.Scene.furniture
	del WindowManager.models_dir


if __name__ == "__main__":
	register()
