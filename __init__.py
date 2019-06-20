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
import subprocess
from bpy.props import *
import bpy.utils.previews
from bpy.types import WindowManager

from .mesh_paint_op import *
from .functions import get_file_dir

def enum_render_scenes(self, context):
	scenes_list = []
	addon_folder = get_file_dir(__file__)
	scenes_dir = os.path.join(addon_folder, "resources", "render_scenes", "*.blend")
	directory_icons = os.path.join(addon_folder, "resources", "render_scenes", "cameras_preview")

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
	path_library = context.window_manager.nexus_model_manager_dir_resource
	library = context.scene.nexus_model_manager.library_list
	path_category = os.path.join(path_library, library)

	return make_list_folder(path_category)

############################ Library ##########################
def make_library_list(self, context):
	path_library = context.window_manager.nexus_model_manager_dir_resource

	return make_list_folder(path_library)

##################################################################
############################ Previews ############################
##################################################################


######### Assets Previews ##########

def enum_previews_asset_items(self, context):
	""" create assets items prewiews """
	enum_items = []

	path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
	category = context.scene.nexus_model_manager.category_list
	library = context.scene.nexus_model_manager.library_list
	directory = os.path.join(path_models, library, category)


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

class Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	path_to_library = bpy.types.Scene.path_to_library = StringProperty(
		name="Path",
		default=os.path.join(os.path.dirname(__file__), "LibraryModels"),
		description="The path to your library",
		subtype="DIR_PATH"
	)

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		col.prop(self, "path_to_library")



#################################################################
############################ Toolbar ############################
#################################################################
class VIEW3D_PT_MainPanel(bpy.types.Panel):
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

class VIEW3D_PT_CreateAsset(bpy.types.Panel):

	bl_label = "Create Asset"
	bl_idname = "VIEW3D_PT_CreateAsset"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Nexus"
	bl_parent_id = "VIEW3D_PT_MainPanel"
	bl_options = {"DEFAULT_CLOSED"}

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def draw(self, context):
		layout = self.layout
		nexus_model_SCN = context.scene.nexus_model_manager
		create_new = nexus_model_SCN.create_new
		
		layout.prop(nexus_model_SCN, "create_new")
		# layout.prop(nexus_model_SCN, "create_asset_dir")
		if create_new:
			layout.prop(nexus_model_SCN, "new_library_name")
			layout.prop(nexus_model_SCN, "new_category_name")			
		else:
			layout.prop(nexus_model_SCN, "library_list", text="Library")
			layout.prop(nexus_model_SCN, "category_list", text="Category")


		layout.prop(nexus_model_SCN, "new_collection_name")

		layout.operator("view3d.create_asset_path", text="Create Asset", icon="NEWFOLDER")

		box = layout.box()

		box.label(text="Settings")
		box.prop(nexus_model_SCN, "apply_cursor_rotation")

		box.prop(nexus_model_SCN, "pack_data", text="Pack data")
		
		col = box.column()
		col.label(text="Render Scene")
		col.scale_y = 1.5
		col.template_icon_view(nexus_model_SCN, "render_scenes", show_labels=True, scale_popup=10)

class VIEW3D_PT_ManagerPreviews(bpy.types.Panel):

	bl_label = "Model Manager"
	bl_idname = "VIEW3D_PT_ManagerPreviews"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Nexus"
	bl_parent_id = "VIEW3D_PT_MainPanel"
	bl_options = {"DEFAULT_CLOSED"}

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def draw(self, context):
		layout = self.layout
		wm = context.window_manager
		nexus_model_SCN = context.scene.nexus_model_manager

		path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
		asset_name = os.path.splitext(nexus_model_SCN.asset_previews)[0]
		category = nexus_model_SCN.category_list
		library = nexus_model_SCN.library_list

		render_path = os.path.join(path_models, library, category, asset_name, "render")


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
		row = box.row()
		row.scale_y = 1.5
		row.template_icon_view(nexus_model_SCN, "asset_previews", show_labels=True, scale_popup=10)
		# row.template_search_preview(nexus_model_SCN, "asset_previews", search_data, "name")

####### Asset Name
		row = box.row()
		row.alignment = "CENTER"
		row.scale_y = 0.5
		row.label(text=asset_name)

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
		col.operator("view3d.model", icon="ADD", text="Add Asset")

class VIEW3D_PT_MeshPaint(bpy.types.Panel):
	bl_label = "Mesh Paint Settings"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Nexus"
	bl_parent_id = "VIEW3D_PT_MainPanel"
	bl_options = {"DEFAULT_CLOSED"}

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"
	
	def draw(self, context):
		layout = self.layout
		nexus_model_SCN = context.scene.nexus_model_manager
		
		layout.prop(nexus_model_SCN, "align_by_normal")
		layout.operator(VIEW3D_OT_MeshPaint.bl_idname, text="Place Asset", icon="SCENE_DATA")
		layout.prop(nexus_model_SCN, "distance_between_asset")

		box = layout.box()
		box.label(text="Random rotation")
		col = box.column(align=True)
		col.prop(nexus_model_SCN, "use_random_rotation")
		if nexus_model_SCN.use_random_rotation:
			col.prop(nexus_model_SCN, "random_rotation_x")
			col.prop(nexus_model_SCN, "random_rotation_y")
			col.prop(nexus_model_SCN, "random_rotation_z")

		box = layout.box()
		box.label(text="Random scale")
		col = box.column(align=True)
		col.prop(nexus_model_SCN, "use_random_scale")
		if nexus_model_SCN.use_random_scale:
			col.prop(nexus_model_SCN, "random_scale_from")
			col.prop(nexus_model_SCN, "random_scale_to")

################################################################
############################ Append ############################
################################################################

class VIEW3D_OT_AddModel(bpy.types.Operator):

	bl_idname = "view3d.model"
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
		path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
		asset_name = nexus_model_SCN.asset_previews
		category = nexus_model_SCN.category_list
		library = nexus_model_SCN.library_list
		is_link = nexus_model_SCN.link_model
		add_dupli_to_sel = nexus_model_SCN.add_duplicollection
		set_to_selected_objects = nexus_model_SCN.set_to_selected_objects

		filepath = os.path.join(path_models, library, category, asset_name, asset_name + ".blend")

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


######################################################################
############################ Library path ############################
######################################################################

class VIEW3D_OT_LibraryPath(bpy.types.Operator):

	bl_idname = "view3d.library_path"
	bl_label = "Library Path"
	
	def execute(self, context):
		filepath = context.window_manager.nexus_model_manager_dir_resource
		bpy.ops.wm.path_open(filepath=filepath)
		return {"FINISHED"}

######################################################################
############################ Asset path ############################
######################################################################

class VIEW3D_OT_AssetPath(bpy.types.Operator):

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

class VIEW3D_OT_CreateAsset(bpy.types.Operator):
	""" Create Asset """
	bl_idname = "view3d.create_asset_path"
	bl_label = "Overwrite file?"

	def draw(self, context):
		layout = self.layout
		layout.label(text="Really?")

	def invoke(self, context, event):

		if not os.path.isfile(bpy.data.filepath):
			self.report({"ERROR"}, "Please save the file!")
			return {"FINISHED"}

		nexus_model_SCN = context.scene.nexus_model_manager
		
		library_dir = context.window_manager.nexus_model_manager_dir_resource #nexus_model_SCN.create_asset_dir
		library_name = None
		category_name = None
		collection_name = nexus_model_SCN.new_collection_name
		create_new = nexus_model_SCN.create_new

		if create_new:
			library_name = nexus_model_SCN.new_library_name
			category_name = nexus_model_SCN.new_category_name
		else:
			library_name = nexus_model_SCN.library_list
			category_name = nexus_model_SCN.category_list

		file_check = os.path.join(library_dir, library_name, category_name, collection_name, collection_name + ".blend")
		if os.path.isfile(file_check):
			return context.window_manager.invoke_confirm(self, event)
		
		return self.execute(context)

	def execute(self, context):
		nexus_model_SCN = context.scene.nexus_model_manager
		
		library_dir = context.window_manager.nexus_model_manager_dir_resource #nexus_model_SCN.create_asset_dir
		library_name = None
		category_name = None
		collection_name = nexus_model_SCN.new_collection_name
		create_new = nexus_model_SCN.create_new
		open_blend_file = nexus_model_SCN.render_scenes

		if create_new:
			library_name = nexus_model_SCN.new_library_name
			category_name = nexus_model_SCN.new_category_name
		else:
			library_name = nexus_model_SCN.library_list
			category_name = nexus_model_SCN.category_list

		asset_dir_path = os.path.join(library_dir, library_name, category_name, collection_name)

		if not os.path.exists(asset_dir_path):
			os.makedirs(asset_dir_path)
			render_path = os.path.join(asset_dir_path, "render")
			os.mkdir(render_path)
			self.report({"INFO"}, "Dirs created: " + asset_dir_path)
		else:
			self.report({"INFO"}, "Dirs already exist" + asset_dir_path)

		collection = None

		if not collection_name in bpy.data.collections:
			collection = bpy.data.collections.new(collection_name)
			bpy.context.scene.collection.children.link(collection)
		else:
			collection = bpy.data.collections[collection_name]
		
		# link selected objects to new collection
		selected_objects = context.selected_objects
		for obj in selected_objects:
			collection.objects.link(obj)

		# save file
		bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

		addon_path = get_file_dir(__file__)
		# empty_blend = os.path.join(addon_path, "resources", "empty.blend")
		append_from_blendfile = bpy.data.filepath

		tools = os.path.join(addon_path, "tools", "create_asset.py")
		
		# get cursor location and roration
		cursor_location = bpy.context.scene.cursor.location.copy()
		cursor_rotation = bpy.context.scene.cursor.rotation_euler.copy()

		cursor_location = "{}|{}|{}".format(cursor_location.x, cursor_location.y, cursor_location.z)
		cursor_rotation = "{}|{}|{}|{}".format(nexus_model_SCN.apply_cursor_rotation, cursor_rotation.x, cursor_rotation.y, cursor_rotation.z)

		# prepeare pack_data variable
		pack_data = nexus_model_SCN.pack_data

		sub = subprocess.Popen(
			[
				bpy.app.binary_path,   # path to blender.exe
				open_blend_file,       # open file
				"-b",                  # open background blender
				"--python",
				tools,                 # path to python script
				append_from_blendfile, # from blendfile append collection
				"Collection",
				collection.name,       # append collection name
				asset_dir_path,        # path save this file
				cursor_location,       # cursor location it is pivot point new asset
				cursor_rotation,       # cursor rotation to new asset
				pack_data             # None or pack file to blend file or save textures to root library
			]
		)

		bpy.data.collections.remove(bpy.data.collections[collection_name])

		return {"FINISHED"}

class VIEW3D_OT_ImagePath(bpy.types.Operator):

	bl_idname = "view3d.image_path"
	bl_label = "Library Image Path"

	def execute(self, context):

		nexus_model_SCN = context.scene.nexus_model_manager
		model_dir = context.window_manager.nexus_model_manager_dir_resource
		library = nexus_model_SCN.library_list
		category = nexus_model_SCN.category_list
		asset_name = nexus_model_SCN.asset_previews

		render_path = os.path.join(model_dir, library, category, asset_name, "render", asset_name + ".png")

		bpy.ops.wm.path_open(filepath=render_path)
		return {"FINISHED"}


class NexusModelManager_WM_Properties(bpy.types.PropertyGroup):

	create_new: BoolProperty(
		name="Create new",
		description="Change behavior create asset and change UI",
		default=False
	)

	new_library_name: StringProperty(
		name="Library",
		description="Name of New Library, if it does not exist",
		default="Awesome_Library"
	)

	new_category_name: StringProperty(
		name="Category",
		description="Name of New Category, if it does not exist",
		default="Awesome_Category"
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
		default=200
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
	VIEW3D_PT_MainPanel,
	VIEW3D_PT_CreateAsset,
	VIEW3D_PT_ManagerPreviews,
	VIEW3D_PT_MeshPaint,
	Preferences,
	VIEW3D_OT_LibraryPath,
	VIEW3D_OT_AssetPath,
	VIEW3D_OT_CreateAsset,
	VIEW3D_OT_ImagePath,
	NexusModelManager_WM_Properties,
	VIEW3D_OT_MeshPaint,
	VIEW3D_OT_AddModel
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	preferences = bpy.context.preferences
	addon_prefs = preferences.addons[__name__].preferences

	WindowManager.nexus_model_manager_dir_resource = StringProperty(
		name="Folder Path",
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

if __name__ == "__main__":
	register()