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
import subprocess
from bpy.props import *
import bpy.utils.previews
from bpy.types import WindowManager

from .mesh_paint_op import *

# separator symbols
sep_lib = "_"
sep_cat = "-"
sep_name = "-"

###########################################################################
#################### function dinamicaly make category ####################
###########################################################################

def make_list_folder(path):

	dirs = os.listdir(path)
	i = 0
	mode_options = []

	for dir in dirs:
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

############################ Collection ##########################
def enum_collections_asset(self, context):

	enum_items = []

	nexus_model_SCN = context.scene.nexus_model_manager
	path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
	filename = nexus_model_SCN.asset_previews
	category = nexus_model_SCN.category_list
	library = nexus_model_SCN.library_list
	assets_name = nexus_model_SCN.asset_previews

	filepath = os.path.join(path_models, library, category, filename, filename + ".blend")
	render_path = os.path.join(path_models, library, category, filename, "render")

	if context is None:
		return enum_items

	pcoll = collections_collection["main"]

	if render_path == pcoll.collection_previews_dir:
		return pcoll.collection_previews

	with bpy.data.libraries.load(filepath) as (df, dt):
		list_collections = df.collections
	list_collections.sort()

	# if render_path and os.path.exists(render_path):
	# 	images_names = []
	# 	for fn in os.listdir(render_path):
	# 		images_names.append(os.path.splitext(fn)[0])

	for i, name in enumerate(list_collections):
		filepath = os.path.join(render_path, name + ".png")

		# icon_name = name.replace(library + sep_lib, "") # remove library name
		# icon_name = icon_name.replace(category + sep_cat, "") # remove category name
		icon_name = name.replace(assets_name + sep_name, "") # remove asset name
		if filepath in pcoll:
			enum_items.append((name, icon_name, "", pcoll[filepath].icon_id, i))
		else:
			thumb = pcoll.load(filepath, filepath, "IMAGE")
			enum_items.append((name, icon_name, "", thumb.icon_id, i))
	# enum_items.sort()

	pcoll.collection_previews = enum_items
	pcoll.collection_previews_dir = render_path
	return pcoll.collection_previews

collections_collection = {}

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
		collection_or_meshdata = nexus_model_SCN.collection_or_meshdata
		collection_asset = os.path.splitext(nexus_model_SCN.collection_asset)[0]
		# collection_asset = collection_asset.replace(library + sep_lib, "")
		# collection_asset = collection_asset.replace(category + sep_cat, "")
		collection_asset = collection_asset.replace(asset_name + sep_name, "")

		render_path = os.path.join(path_models, library, category, asset_name, "render")

		# with bpy.data.libraries.load(filepath) as (df, dt):
		# 	list_collections = df.collections
		if os.path.exists(render_path):
			num_collections = len(os.listdir(render_path)) > 1
		else:
			num_collections = False

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
		row.template_icon_view(nexus_model_SCN, "asset_previews", show_labels=True)

####### Asset Name
		row = box.row()
		row.alignment = "CENTER"
		row.scale_y = 0.5
		row.label(text=asset_name)

####### Previews scale
		# col = box.column()
		# col.prop(nexus_model_SCN, "scale_preview", slider=True)

####### Collections list
		if num_collections:
			row = box.row()
			col = row.column()
			# col.scale_y = nexus_model_SCN.scale_preview
			col.scale_y = 1.5
			col.template_icon_view(nexus_model_SCN, "collection_asset", show_labels=True)
			# col = row.column()
			# col.operator("preview.big_preview", icon="ZOOM_IN", text="")
####### Collection Name
			row = box.row()
			row.alignment = "CENTER"
			row.scale_y = 0.5
			row.label(text=collection_asset.replace(asset_name + "_", ""))

####### Collection or mesh data
		row = box.row()
		row.label(text="What add?")
		row = box.row()
		row.prop(nexus_model_SCN, "collection_or_meshdata", expand=True)

		if collection_or_meshdata == "COLLECTION": ####################################### COLLECTION
####### Add location
			row = box.row()
			row.label(text="Add location")
			row = box.row()
			row.prop(nexus_model_SCN, "add_location", expand=True)

####### link and dupli
			col = box.column()
			row = col.row()
			row.prop(nexus_model_SCN, "link_model")
			row.prop(nexus_model_SCN, "add_duplicollection")

####### instance collections
			col = box.column()
			row = col.row()
			row.enabled = nexus_model_SCN.link_model
			row.prop(nexus_model_SCN, "instance_collections")
		elif collection_or_meshdata == "MESH": ########################################### MESH
####### link and dupli
			col = box.column()
			col.prop(nexus_model_SCN, "link_model")
			col.prop(nexus_model_SCN, "set_to_selected_objects")

		elif collection_or_meshdata == "OBJECT": ####################################### OBJECT
####### Add location
			row = box.row()
			row.label(text="Add location")
			row = box.row()
			row.prop(nexus_model_SCN, "add_location", expand=True)


####### link and dupli
			col = box.column()
			row = col.row()
			row.prop(nexus_model_SCN, "link_model")

####### Add Button
		col = box.column(align=True)
		col.operator("view3d.model", icon="ADD", text="Add Asset")

class VIEW3D_PT_MeshPaint(bpy.types.Panel):
	bl_label = "Mesh Paint Settings"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Nexus Model Manager"
	bl_parent_id = "VIEW3D_PT_MainPanel"
	bl_options = {"DEFAULT_CLOSED"}

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"
	
	def draw(self, context):
		layout = self.layout

		layout.operator(VIEW3D_OT_MeshPaint.bl_idname, text="Mesh Paint", icon="STYLUS_PRESSURE")

	

# class BigPreview(bpy.types.Operator):
# 	bl_idname = "preview.big_preview"
# 	bl_label = "Big Preview"

# 	def execute(self, context):
# 		print("Running big preview")
# 		return {"FINISHED"}

# 	def check(self, context):
# 		return False

# 	def invoke(self, context, event):
# 		wm = context.window_manager
# 		print("Invoke big preview")
# 		return wm.invoke_props_dialog(self, width=800, height=800)

# 	def draw(self, context):
# 		layout = self.layout
# 		nexus_model_SCN = context.scene.nexus_model_manager
# 		col = layout.column()
# 		col.scale_y = 5
# 		col.template_icon_view(nexus_model_SCN, "collection_asset", show_labels=True)

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

	def invoke(self, context, event):
		nexus_model_SCN = context.scene.nexus_model_manager
		collection_name = nexus_model_SCN.collection_asset
		is_link = nexus_model_SCN.link_model
		add_dupli_to_sel = nexus_model_SCN.add_duplicollection

		if not is_link and add_dupli_to_sel and nexus_model_SCN.add_location == "CURSOR":
			self.report({"INFO"}, "Set Add location to Center")
			nexus_model_SCN.add_location = "CENTER"

		if bpy.data.collections.get(collection_name) is not None:
			bpy.ops.object.collection_instance_add(collection=collection_name)
			self.report({"INFO"}, "Added Intance collection from scene (allready exist in scene)")
			# return context.window_manager.invoke_props_dialog(self)
		else:
			self.execute(context)
		
		return {"FINISHED"}


	def execute(self, context):
		nexus_model_SCN = context.scene.nexus_model_manager
		path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
		filename = nexus_model_SCN.asset_previews
		category = nexus_model_SCN.category_list
		library = nexus_model_SCN.library_list
		collection_name = nexus_model_SCN.collection_asset
		is_link = nexus_model_SCN.link_model
		inst_collections = nexus_model_SCN.instance_collections
		add_dupli_to_sel = nexus_model_SCN.add_duplicollection
		collection_or_meshdata = nexus_model_SCN.collection_or_meshdata
		set_to_selected_objects = nexus_model_SCN.set_to_selected_objects

		filepath = os.path.join(path_models, library, category, filename, filename + ".blend")

		if collection_or_meshdata == "COLLECTION":
			directory_inside_file = os.path.join(filepath, "Collection")
		elif collection_or_meshdata == "MESH":
			directory_inside_file = os.path.join(filepath, "Mesh")
			collection_name = "SM_" + collection_name
		elif collection_or_meshdata == "OBJECT":
			directory_inside_file = os.path.join(filepath, "Object")
			collection_name = "SM_" + collection_name
		else:
			print("----------------- SOMETHING ERROR >> collection_or_meshdata << -----------------")

		filepath_collection_name = directory_inside_file + collection_name


		selected_objects = context.selected_objects

		if not add_dupli_to_sel:
			bpy.ops.object.select_all(action="DESELECT")

		if is_link:
			bpy.ops.wm.link(
				filepath=filepath_collection_name,
				filename=collection_name,
				directory=directory_inside_file,
				link=True,
				instance_collections=inst_collections,
				autoselect=True
			)
		else:
			bpy.ops.wm.append(
				filepath=filepath_collection_name,
				filename=collection_name,
				directory=directory_inside_file,
				link=False,
				instance_collections=False,
				autoselect=True
			)

		if collection_or_meshdata == "COLLECTION":
			if add_dupli_to_sel:
				collection = bpy.data.collections[collection_name]
				for obj in selected_objects:
					obj.dupli_collection = collection
					obj.dupli_type = "COLLECTION"

			if len(bpy.context.selected_objects) > 0:
				if nexus_model_SCN.add_location == "CURSOR":
					bpy.context.selected_objects[0].location = context.scene.cursor.location
				else:
					bpy.context.selected_objects[0].location = (0.0, 0.0, 0.0)

		elif collection_or_meshdata == "MESH":
			if set_to_selected_objects:
				mesh = bpy.data.meshes[collection_name]
				for obj in selected_objects:
					if obj.type == "MESH":
						obj.data = mesh

		elif collection_or_meshdata == "OBJECT":
			if len(bpy.context.selected_objects) > 0:
				if nexus_model_SCN.add_location == "CURSOR":
					bpy.context.selected_objects[0].location = context.scene.cursor.location
				else:
					bpy.context.selected_objects[0].location = (0.0, 0.0, 0.0)

		# if add_dupli_to_sel:
		# 	collection = bpy.data.collections[collection_name]
		# 	for obj in selected_objects:
		# 		obj.dupli_collection = collection
		# 		obj.dupli_type = "COLLECTION"

		# if is_link and not inst_collections:
		# 	return {"FINISHED"}



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

	bl_idname = "view3d.create_asset_path"
	bl_label = "Create Asset Path"
	
	def execute(self, context):
		nexus_model_SCN = context.scene.nexus_model_manager
		
		library_dir = context.window_manager.nexus_model_manager_dir_resource #nexus_model_SCN.create_asset_dir
		library_name = ""
		category_name = ""
		collection_name = nexus_model_SCN.new_collection_name
		create_new = nexus_model_SCN.create_new

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
			check_file = os.path.join(asset_dir_path, collection_name + ".blend")
			if os.path.isfile(check_file):
				self.report({"INFO"}, "File exist! Interupt script!")
				return {"FINISHED"}

			self.report({"INFO"}, "Dirs already exist" + asset_dir_path)

		collection = ""

		if not collection_name in bpy.data.collections:
			collection = bpy.data.collections.new(collection_name)
			bpy.context.scene.collection.children.link(collection)
		else:
			collection = bpy.data.collections[collection_name]

		# move active object to root collection
		#bpy.ops.object.move_to_collection(collection_index=0)
		
		# link selected objects to new collection
		selected_objects = context.selected_objects
		for obj in selected_objects:
			collection.objects.link(obj)
			# unlink active object from root collection
			#context.scene.collection.objects.unlink(obj)

		#context.scene.collection.objects.unlink(context.active_object)
		#context.active_object.name = collection_name

		# save file
		bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

		addon_path = get_file_dir(__file__)
		empty_blend = os.path.join(addon_path, "resources", "empty.blend")
		append_from_blendfile = bpy.data.filepath

		tools = os.path.join(addon_path, "tools", "create_asset.py")
		
		# get cursor location
		cursor_location = bpy.context.scene.cursor.location.copy()

		cursor_location = "{}|{}|{}".format(cursor_location.x, cursor_location.y, cursor_location.z)

		sub = subprocess.Popen(
			[
				bpy.app.binary_path,   # path to blender.exe
				empty_blend,           # open file
				"-b",                  # open background blender
				"--python",
				tools,                 # path to python script
				append_from_blendfile, # from blendfile append collection
				"Collection",
				collection.name,       # append collection name
				asset_dir_path,        # path save this file
				cursor_location        # cursor location it is pivot point new asset
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
		selected_preview = nexus_model_SCN.asset_previews
		collection = nexus_model_SCN.collection_asset

		render_path = os.path.join(model_dir, library, category, selected_preview, "render")

		if os.path.exists(render_path):
			num_collections = len(os.listdir(render_path)) > 1
		else:
			num_collections = False

		if num_collections:
			# collection = library + sep_lib + category + sep_cat + collection
			filepath = os.path.join(model_dir, library, category, selected_preview, "render", collection + ".png")
		else:
			collection = collection.replace(library + sep_lib, "")
			collection = collection.replace(category + sep_cat, "")
			filepath = os.path.join(model_dir, library, category, selected_preview, "render", collection + ".png")

		bpy.ops.wm.path_open(filepath=filepath)
		return {"FINISHED"}


class NexusModelManager_WM_Properties(bpy.types.PropertyGroup):

	# scale_preview = FloatProperty(
	# 	name="Scale preview",
	# 	default=1.5,
	# 	min=1.0,
	# 	max=10.0,
	# 	soft_min=1.0,
	# 	soft_max=10.0
	# )

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

	# create_asset_dir: StringProperty(
	# 	name="Library Dir",
	# 	subtype="DIR_PATH",
	# 	default=os.path.join(get_file_dir(__file__), "LibraryModels")
	# )

	link_model: BoolProperty(
		name="Link",
		description="If True link model else append model",
		default=False
	)

	instance_collections: BoolProperty(
		name="Instance collections",
		description="Instance collections",
		default=False
	)

	set_to_selected_objects: BoolProperty(
		name="Set to selected objects",
		description="Set mesh data to selected objects",
		default=False
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

	collection_asset: EnumProperty(
		items=enum_collections_asset
	)

	collection_or_meshdata: EnumProperty(
		name="Collection or Mesh Data",
		items=[
			("COLLECTION", "Collection", "", 0),
			("MESH", "Mesh Data", "", 1),
			("OBJECT", "Object", "", 2)
		],
		default = "COLLECTION"
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

	# bpy.utils.register_class(Preferences)
	# bpy.utils.register_class(Library_Path)
	# bpy.utils.register_class(Asset_Path)
	# bpy.utils.register_class(Image_Path)
	# # bpy.utils.register_class(AddExistCollection)
	# bpy.utils.register_module(__name__)


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
	pcoll.collection_previews_dir = ""
	pcoll.collection_previews = ()

	collections_collection["main"] = pcoll

	bpy.types.Scene.nexus_model_manager = bpy.props.PointerProperty(type=NexusModelManager_WM_Properties)


######################################################################
############################# Unregister #############################
######################################################################

def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)

	# bpy.utils.unregister_class(Preferences)
	# bpy.utils.unregister_class(Library_Path)
	# bpy.utils.unregister_class(Asset_Path)
	# bpy.utils.unregister_class(Image_Path)
	# bpy.utils.unregister_class(AddExistCollection)

	# del WindowManager.nexus_model_manager_dir_resource
	# del bpy.types.Scene.nexus_model_manager

	for pcoll in asset_collections.values():
		bpy.utils.previews.remove(pcoll)
	asset_collections.clear()

	for pcoll in collections_collection.values():
		bpy.utils.previews.remove(pcoll)
	collections_collection.clear()

	# bpy.utils.unregister_module(__name__)



if __name__ == "__main__":
	register()
