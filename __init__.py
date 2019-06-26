bl_info = {
	"name": "Nexus Model Manager",
	"author": "Nexus Studio",
	"version": (0, 9, 0),
	"blender": (2, 80, 0),
	"location": "View 3D > Tool Shelf",
	"description": "Tools",
	"warning": "",
	"wiki_url": "https://github.com/Hichigo/NexusModelManager",
	"category": "Object"
	}

import bpy
import os
import glob

from bpy.props import *
import bpy.utils.previews
from bpy.types import AddonPreferences, WindowManager, Panel, Operator, PropertyGroup

from .CreateAsset.create_asset_op import *
from .CreateAsset.create_asset_pt import *

from .MeshPaint.mesh_paint_op import *
from .MeshPaint.mesh_paint_pt import *

from .random_list_ui import *

from .functions import get_addon_dir, get_addon_prefs

def filter_on_mesh_prop(self, object):
    return object.type == "MESH"

def enum_render_scenes(self, context):
	scenes_list = []
	addon_folder = get_addon_dir()
	addon_prefs = get_addon_prefs()
	scenes_dir = os.path.join(addon_prefs.path_to_render_scenes, "*.blend")
	directory_icons = os.path.join(addon_prefs.path_to_render_scenes, "cameras_preview")

	if context is None:
		return scenes_list

	pcoll = render_scene_collections["main"]

	if directory_icons == pcoll.render_scene_previews_dir:
		return pcoll.render_scene

	scene_files_path = glob.glob(scenes_dir)

	for i, scene_file_path in enumerate(scene_files_path):
		if os.path.isfile(scene_file_path):
			file_name = os.path.split(scene_file_path)[1] # get file name without path
			file_name = file_name.split(".")[0] # get file name without extension
			icon_path = os.path.join(directory_icons, file_name + ".png")
			
			if icon_path in pcoll:
				scenes_list.append((scene_file_path, file_name, "", pcoll[icon_path].icon_id, i))
			else:
				thumb = pcoll.load(icon_path, icon_path, "IMAGE")
				scenes_list.append((scene_file_path, file_name, "", thumb.icon_id, i))

	scenes_list.sort()

	pcoll.render_scene = scenes_list
	pcoll.render_scene_previews_dir = directory_icons
	return pcoll.render_scene

render_scene_collections = {}

###########################################################################
#################### function dinamicaly make category ####################
###########################################################################

def make_list_folder(path):

	dirs = os.listdir(path)
	i = 0
	mode_options = []

	for dir in dirs:
		if dir != "textures":
			if os.path.isdir(os.path.join(path, dir)):
				item = (dir, dir, "", i)
				mode_options.append(item)
				i += 1

	return mode_options

############################ Category ##########################
def make_category_list(self, context):
	library_dir = context.window_manager.nexus_model_manager_dir_resource
	library = context.scene.nexus_model_manager.library_list
	path_category = os.path.join(library_dir, library)

	return make_list_folder(path_category)

############################ Library ##########################
def make_library_list(self, context):
	library_dir = context.window_manager.nexus_model_manager_dir_resource

	return make_list_folder(library_dir)

##################################################################
############################ Previews ############################
##################################################################

######### Assets Previews ##########

def enum_previews_asset_items(self, context):
	""" create assets items prewiews """
	enum_items = []

	library_dir = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
	category = context.scene.nexus_model_manager.category_list
	library = context.scene.nexus_model_manager.library_list
	directory = os.path.join(library_dir, library, category)


	if context is None:
		return enum_items

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
				thumb = pcoll.load(filepath, filepath, "IMAGE")
				enum_items.append((name, name, "", thumb.icon_id, i))
	enum_items.sort()

	pcoll.asset_previews = enum_items
	pcoll.asset_previews_dir = directory
	return pcoll.asset_previews

asset_collections = {}

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

class VIEW3D_PT_ManagerPreviews(Panel):

	bl_label = "Model Manager"
	bl_idname = "VIEW3D_PT_ManagerPreviews"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Nexus"
	bl_parent_id = "VIEW3D_PT_MainPanel"

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def draw(self, context):
		addon_prefs = get_addon_prefs()
		layout = self.layout
		wm = context.window_manager
		nexus_model_SCN = context.scene.nexus_model_manager

		library_dir = context.window_manager.nexus_model_manager_dir_resource
		asset_name = os.path.splitext(nexus_model_SCN.asset_previews)[0]
		category = nexus_model_SCN.category_list
		library = nexus_model_SCN.library_list

		render_path = os.path.join(library_dir, library, category, asset_name, "render")

############## Panel ##############

		box = layout.box()
		box.label(text="Model Manager")

####### Drop Down Menu library
		row = box.row()
		row.label(text="Library")
		row.prop(nexus_model_SCN, "library_list", text="")

####### Drop Down Menu category
		row = box.row()
		row.label(text="Category")
		row.prop(nexus_model_SCN, "category_list", text="")

####### Asset folder button
		col = box.column()
		row = col.row(align=True)
		row.operator("view3d.asset_path", icon="FILE_FOLDER", text="Open Asset Folder")
		row.operator("view3d.image_path", icon="FILE_IMAGE", text="Open Image")

####### Previews
		col = box.column()
		col.scale_y = 1.5
		col.template_icon_view(nexus_model_SCN, "asset_previews", show_labels=True, scale_popup=addon_prefs.preview_asset_scale)
		# col.template_ID_preview(asset_collections["main"].asset_previews, "name", rows=3, cols=8)
		# col.template_search_preview(nexus_model_SCN, "asset_previews", search_data, "name")
		col.label(text=asset_name)

		row = box.row()
		row.operator("view3d.search_asset", icon="VIEWZOOM", text="Search Asset")

# ####### Add location
		row = box.row()
		row.label(text="Add location")
		row = box.row()
		row.prop(nexus_model_SCN, "add_location", expand=True)

####### link and dupli
		col = box.column()
		row = col.row()
		row.prop(nexus_model_SCN, "link_model")
		row = col.row()
		row.enabled = nexus_model_SCN.link_model
		row.prop(nexus_model_SCN, "add_duplicollection")

####### Add Button
		col = box.column(align=True)
		col.operator("view3d.add_model", icon="ADD", text="Add Asset")

################################################################
############################ Append ############################
################################################################

class VIEW3D_OT_AddModel(Operator):

	bl_idname = "view3d.add_model"
	bl_label = "Add Model?"

	# def draw(self, context):
	# 	layout = self.layout
	# 	col = layout.column()
	# 	col.label("The asset is already added. Add more?")

	# def invoke(self, context, event):
	# 	nexus_model_SCN = context.scene.nexus_model_manager
	# 	collection_name = nexus_model_SCN.asset_previews
	# 	is_link = nexus_model_SCN.link_model
	# 	add_dupli_to_sel = nexus_model_SCN.add_duplicollection

	# 	if not is_link and add_dupli_to_sel and nexus_model_SCN.add_location == "CURSOR":
	# 		self.report({"INFO"}, "Set Add location to Center")
	# 		nexus_model_SCN.add_location = "CENTER"

	# 	if bpy.data.collections.get(collection_name) is not None:
	# 		bpy.ops.object.collection_instance_add(collection=collection_name)
	# 		self.report({"INFO"}, "Added Intance collection from scene (allready exist in scene)")
	# 		# return context.window_manager.invoke_props_dialog(self)
	# 	else:
	# 		self.execute(context)
		
	# 	return {"FINISHED"}


	def execute(self, context):
		nexus_model_SCN = context.scene.nexus_model_manager
		library_dir = context.window_manager.nexus_model_manager_dir_resource
		asset_name = nexus_model_SCN.asset_previews
		category = nexus_model_SCN.category_list
		library = nexus_model_SCN.library_list
		is_link = nexus_model_SCN.link_model
		add_dupli_to_sel = nexus_model_SCN.add_duplicollection
		set_to_selected_objects = nexus_model_SCN.set_to_selected_objects

		filepath = os.path.join(library_dir, library, category, asset_name, asset_name + ".blend")

		directory_inside_file = os.path.join(filepath, "Collection")

		filepath_collection_name = directory_inside_file + asset_name


		selected_objects = context.selected_objects

		# if not add_dupli_to_sel:
		bpy.ops.object.select_all(action="DESELECT")

		if is_link:
			bpy.ops.wm.link(
				filepath=filepath_collection_name,
				filename=asset_name,
				directory=directory_inside_file,
				link=True,
				instance_collections=True,
				autoselect=True
			)
		else:
			bpy.ops.wm.append(
				filepath=filepath_collection_name,
				filename=asset_name,
				directory=directory_inside_file,
				link=False,
				instance_collections=False,
				autoselect=True
			)

		if is_link:
			if add_dupli_to_sel:
				collection = bpy.data.collections[asset_name]
				bpy.data.objects.remove(context.active_object)
				for obj in selected_objects:
					obj.instance_type = "COLLECTION"
					obj.instance_collection = collection

		if len(bpy.context.selected_objects) > 0:
			if is_link:
				if nexus_model_SCN.add_location == "CURSOR":
					bpy.context.selected_objects[0].location = context.scene.cursor.location
				else:
					bpy.context.selected_objects[0].location = (0.0, 0.0, 0.0)
			else:
				if nexus_model_SCN.add_location == "CURSOR":
					bpy.context.selected_objects[0].parent.location = context.scene.cursor.location
				else:
					bpy.context.selected_objects[0].parent.location = (0.0, 0.0, 0.0)

		return {"FINISHED"}

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

	bl_idname = "view3d.library_path"
	bl_label = "Library Path"
	
	def execute(self, context):
		library_dir = context.window_manager.nexus_model_manager_dir_resource
		bpy.ops.wm.path_open(filepath=library_dir)
		return {"FINISHED"}

######################################################################
############################ Asset path ############################
######################################################################

class VIEW3D_OT_AssetPath(Operator):

	bl_idname = "view3d.asset_path"
	bl_label = "Library Asset Path"

	def execute(self, context):

		nexus_model_SCN = context.scene.nexus_model_manager
		model_dir = context.window_manager.nexus_model_manager_dir_resource
		library = nexus_model_SCN.library_list
		category = nexus_model_SCN.category_list
		selected_preview = nexus_model_SCN.asset_previews

		filepath = os.path.join(model_dir, library, category, selected_preview)

		bpy.ops.wm.path_open(filepath=filepath)
		return {"FINISHED"}

class VIEW3D_OT_ImagePath(Operator):

	bl_idname = "view3d.image_path"
	bl_label = "Library Image Path"

	def execute(self, context):

		nexus_model_SCN = context.scene.nexus_model_manager
		library_dir = context.window_manager.nexus_model_manager_dir_resource
		library = nexus_model_SCN.library_list
		category = nexus_model_SCN.category_list
		asset_name = nexus_model_SCN.asset_previews

		render_path = os.path.join(library_dir, library, category, asset_name, "render", asset_name + ".png")

		bpy.ops.wm.path_open(filepath=render_path)
		return {"FINISHED"}

class VIEW3D_OT_SearchAsset(Operator):
	bl_idname = "view3d.search_asset"
	bl_label = "Search Asset"
	bl_property = "search_asset"

	search_asset: EnumProperty(
		name="Search Asset",
		items=enum_previews_asset_items,
	)

	def execute(self, context):
		nexus_model_SCN = context.scene.nexus_model_manager
		nexus_model_SCN.asset_previews = self.search_asset
		return {"FINISHED"}

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {"RUNNING_MODAL"}

class SCENE_OT_AddListItem(Operator):
	bl_idname = "scene.add_list_item"
	bl_label = "Add Item"
	bl_property = "search_asset"

	search_asset: EnumProperty(
		name="Search Asset",
		items=enum_previews_asset_items,
	)

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {"RUNNING_MODAL"}

	def execute(self, context):
		random_asset_list = context.scene.random_asset_list
		new_index = len(random_asset_list.list_item)
		asset_name = self.search_asset
		if new_index > 0: # if list items not empty, check item exists
			if random_asset_list.list_item.find(asset_name) != -1:
				self.report({"INFO"}, "This asset exists in list!")
				return {"CANCELLED"}

		# create new item
		random_asset_list.list_item.add()
		
		# set item name
		random_asset_list.list_item[new_index].name = asset_name

		# make path to asset
		nexus_model_SCN = context.scene.nexus_model_manager
		library_dir = context.window_manager.nexus_model_manager_dir_resource
		
		library = nexus_model_SCN.library_list
		category = nexus_model_SCN.category_list

		filepath_to_asset = os.path.join(library_dir, library, category, asset_name, asset_name + ".blend")

		# set filepath to asset
		random_asset_list.list_item[new_index].path_to_asset = filepath_to_asset

		# set active index
		random_asset_list.active_index = new_index
		
		return {'FINISHED'}

class SCENE_OT_RemoveListItem(Operator):
	bl_idname = "scene.remove_list_item"
	bl_label = "Remove Item"


	def execute(self, context):
		random_asset_list = context.scene.random_asset_list
		remove_index = random_asset_list.active_index
		
		# remove item
		random_asset_list.list_item.remove(remove_index)

		return {'FINISHED'}

class NexusModelManager_WM_Properties(PropertyGroup):

	canvas_object: PointerProperty(
		name="Canvas",
		description="If empty then will draw over all objects. APPLY TRANSFORM TO OBJECT!!!",
        type=bpy.types.Object,
        poll=filter_on_mesh_prop
    )

	use_random_asset: BoolProperty(
		name="Use random asset",
		description="If True get asset from list",
		default=False
	)

	new_collection_name: StringProperty(
		name="Collection",
		description="Name of New Collection",
		default="Awesome_Collection"
	)

	align_by_normal: BoolProperty(
		name="Align by Normal",
		description="Align asset by normal",
		default=True
	)

	apply_cursor_rotation: BoolProperty(
		name="Apply 3D Cursor Rotation",
		description="Apply 3D Cursor Rotation to New Asset",
		default=True
	)

	link_model: BoolProperty(
		name="Link",
		description="If True link model else append model",
		default=True
	)

	set_to_selected_objects: BoolProperty(
		name="Set to selected objects",
		description="Set mesh data to selected objects",
		default=False
	)

	distance_between_asset: FloatProperty(
		name="Distance",
		description="Distance to which assets can be placed",
		min=0,
		default=2
	)

	use_random_rotation: BoolProperty(
		name="Use random rotation",
		description="Set random rotation to asset",
		default=False
	)

	random_rotation_x: FloatProperty(
		name="X",
		description="Random rotation by X",
		min=0,
		max=359,
		default=0
	)
	random_rotation_y: FloatProperty(
		name="Y",
		description="Random rotation by Y",
		min=0,
		max=359,
		default=0
	)
	random_rotation_z: FloatProperty(
		name="Z",
		description="Random rotation by Z",
		min=0,
		max=359,
		default=0
	)

	use_random_scale: BoolProperty(
		name="Use random scale",
		description="Set random scale to asset",
		default=False
	)
	random_scale_from: FloatProperty(
		name="From",
		description="Random scale from",
		min=0,
		default=1
	)
	random_scale_to: FloatProperty(
		name="To",
		description="Random scale to",
		min=0,
		default=2
	)

	asset_previews: EnumProperty(
		items=enum_previews_asset_items
	)

	library_list: EnumProperty(
		items=make_library_list
	)

	category_list: EnumProperty(
		items=make_category_list
	)

	render_scenes: EnumProperty(
		items=enum_render_scenes
	)

	pack_data: EnumProperty(
		name="Pack data",
		items=[
			("NONE", "None", "", 0),
			("PACK", "Pack to .blend", "", 1),
			("TEXTURE", "Texture to library", "", 2)
		],
		default = "NONE"
	)

	add_location: EnumProperty(
		name="Add location",
		items=[
			("CENTER", "Center", "", 0),
			("CURSOR", "Cursor", "", 1)
		],
		default = "CENTER"
	)

	add_duplicollection: BoolProperty(
		name="Add duplicollection to selected",
		description="Add duplicollection to selected objects",
		default=False
	)

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