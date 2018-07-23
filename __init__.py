bl_info = {
	"name": "Nexus Model Manager",
	"author": "Nexus Studio",
	"version": (0, 9, 0),
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
	path_library = context.window_manager.nexus_model_manager_dir_resource
	library = context.window_manager.nexus_model_manager.library_list
	path_category = os.path.join(path_library, library)

	return make_list_folder(path_category)

############################ Library ##########################
def make_library_list(self, context):
	path_library = context.window_manager.nexus_model_manager_dir_resource

	return make_list_folder(path_library)

############################ Group ##########################
def enum_groups_asset(self, context):

	enum_items = []

	nexus_model_WM = bpy.data.window_managers["WinMan"].nexus_model_manager
	path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
	filename = nexus_model_WM.asset_previews
	category = nexus_model_WM.category_list
	library = nexus_model_WM.library_list

	filepath = os.path.join(path_models, library, category, filename, filename + ".blend")
	render_path = os.path.join(path_models, library, category, filename, "render")

	if context is None:
		return enum_items

	pcoll = groups_collection["main"]

	if render_path == pcoll.group_previews_dir:
		return pcoll.group_previews

	# with bpy.data.libraries.load(filepath) as (df, dt):
	# 	list_groups = df.groups

	if render_path and os.path.exists(render_path):
		images_names = []
		for fn in os.listdir(render_path):
			images_names.append(os.path.splitext(fn)[0])

	for i, name in enumerate(images_names):
		filepath = os.path.join(render_path, name + ".png")

		if filepath in pcoll:
			enum_items.append((name, name, "", pcoll[filepath].icon_id, i))
		else:
			thumb = pcoll.load(filepath, filepath, 'IMAGE')
			enum_items.append((name, name, "", thumb.icon_id, i))
	enum_items.sort()

	pcoll.group_previews = enum_items
	pcoll.group_previews_dir = render_path
	return pcoll.group_previews

groups_collection = {}

##################################################################
############################ Previews ############################
##################################################################


######### Assets Previews ##########

def enum_previews_asset_items(self, context):
	""" create assets items prewiews """
	enum_items = []

	path_models = bpy.data.window_managers['WinMan'].nexus_model_manager_dir_resource
	category = bpy.data.window_managers['WinMan'].nexus_model_manager.category_list
	library = bpy.data.window_managers["WinMan"].nexus_model_manager.library_list
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


class ManagerPreviewsPanel(bpy.types.Panel):

	bl_label = "Nexus Model Manager"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Nexus Model Manager"

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def draw(self, context):
		layout = self.layout
		wm = context.window_manager
		nexus_model_WM = bpy.data.window_managers["WinMan"].nexus_model_manager
		nexus_model_WM = wm.nexus_model_manager

		path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
		asset_name = nexus_model_WM.asset_previews
		category = nexus_model_WM.category_list
		library = nexus_model_WM.library_list

		render_path = os.path.join(path_models, library, category, asset_name, "render")

		# with bpy.data.libraries.load(filepath) as (df, dt):
		# 	list_groups = df.groups

		num_groups = len(os.listdir(render_path)) > 1

############## Panel ##############

############## Library folder button ##############

		box = layout.box()
		box.label(text="Library Folder:")
		col = box.column(align=True)
		col.prop(wm, "nexus_model_manager_dir_resource")
		col.operator("library.library_path", icon="FILE_FOLDER", text="Open Library Folder")



		box = layout.box()
		box.label(text="Model Manager")

####### Drop Down Menu library
		row = box.row()
		row.label(text="Library")
		row.prop(nexus_model_WM, "library_list", text="")

####### Drop Down Menu category
		row = box.row()
		row.label(text="Category")
		row.prop(nexus_model_WM, "category_list", text="")

####### Previews
		row = box.row()
		row.template_icon_view(nexus_model_WM, "asset_previews", show_labels=True)

####### Asset Name
		row = box.row()
		row.alignment = 'CENTER'
		row.scale_y = 0.5
		row.label(os.path.splitext(asset_name)[0])

####### Previews scale
		# col = box.column()
		# col.prop(nexus_model_WM, "scale_preview", slider=True)

####### Groups list
		if num_groups:
			row = box.row()
			col = row.column()
			# col.scale_y = nexus_model_WM.scale_preview
			col.template_icon_view(nexus_model_WM, "group_asset", show_labels=True)
			col = row.column()
			col.operator("preview.big_preview", icon="ZOOM_IN", text="")

####### Asset folder button
		col = box.column()
		col.operator("library.asset_path", icon="FILE_FOLDER", text="Open Asset Folder")

####### Add location
		row = box.row()
		row.label("Add location")
		row = box.row()
		row.prop(nexus_model_WM, "add_location", expand=True)

####### link and dupli
		col = box.column()
		row = col.row()
		row.prop(nexus_model_WM, "link_model")
		row.prop(nexus_model_WM, "add_dupligroup")

####### instance groups
		col = box.column()
		row = col.row()
		row.enabled = nexus_model_WM.link_model
		row.prop(nexus_model_WM, "instance_groups")

####### Add Button
		col = box.column(align=True)
		col.operator("add.model", icon="ZOOMIN", text="Add Asset")


class BigPreview(bpy.types.Operator):
	bl_idname = "preview.big_preview"
	bl_label = "Big Preview"

	def execute(self, context):
		print("Running big preview")
		return {'FINISHED'}

	def check(self, context):
		return False

	def invoke(self, context, event):
		wm = context.window_manager
		print("Invoke big preview")
		return wm.invoke_props_dialog(self, width=800, height=800)

	def draw(self, context):
		layout = self.layout
		nexus_model_WM = context.window_manager.nexus_model_manager
		col = layout.column()
		col.scale_y = 5
		col.template_icon_view(nexus_model_WM, "group_asset", show_labels=True)

################################################################
############################ Append ############################
################################################################

class AddModelOperator(bpy.types.Operator):

	bl_idname = "add.model"
	bl_label = "Add Model?"

	def draw(self, context):
		layout = self.layout
		nexus_model_WM = context.window_manager.nexus_model_manager
		col = layout.column()
		col.label("The asset is already added. Add more?")

	def invoke(self, context, event):
		nexus_model_WM = bpy.data.window_managers["WinMan"].nexus_model_manager
		group_name = nexus_model_WM.group_asset
		is_link = nexus_model_WM.link_model
		add_dupli_to_sel = nexus_model_WM.add_dupligroup

		if not is_link and add_dupli_to_sel and nexus_model_WM.add_location == "CURSOR":
			self.report({'INFO'}, 'Set Add location to "Center"')
			nexus_model_WM.add_location = "CENTER"

		if bpy.data.groups.get(group_name) is not None:
			return context.window_manager.invoke_props_dialog(self)
		else:
			self.execute(context)
		
		return {'FINISHED'}


	def execute(self, context):
		
		scn = context.scene
		nexus_model_WM = bpy.data.window_managers["WinMan"].nexus_model_manager
		path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
		filename = nexus_model_WM.asset_previews
		category = nexus_model_WM.category_list
		library = nexus_model_WM.library_list
		group_name = nexus_model_WM.group_asset
		is_link = nexus_model_WM.link_model
		inst_groups = nexus_model_WM.instance_groups
		add_dupli_to_sel = nexus_model_WM.add_dupligroup

		filepath = os.path.join(path_models, library, category, filename, filename + ".blend")
		filepath_group = os.path.join(filepath, "Group")
		filepath_group_name = filepath_group + group_name


		selected_objects = context.selected_objects

		if not add_dupli_to_sel:
			bpy.ops.object.select_all(action='DESELECT')


		if is_link:
			bpy.ops.wm.link(
				filepath=filepath_group_name,
				filename=group_name,
				directory=filepath_group,
				link=True,
				instance_groups=inst_groups
			)
		else:
			bpy.ops.wm.append(
				filepath=filepath_group_name,
				filename=group_name,
				directory=filepath_group,
				link=False,
				instance_groups=False
			)

		if add_dupli_to_sel:
			group = bpy.data.groups[group_name]
			for obj in selected_objects:
				obj.dupli_group = group
				obj.dupli_type = 'GROUP'

		if is_link and not inst_groups:
			return {'FINISHED'}

		if len(bpy.context.selected_objects) > 0:
			if nexus_model_WM.add_location == "CURSOR":
				bpy.context.selected_objects[0].location = context.scene.cursor_location
			else:
				bpy.context.selected_objects[0].location = (0.0, 0.0, 0.0)

		return {'FINISHED'}


######################################################################
############################ Library path ############################
######################################################################

class Library_Path(bpy.types.Operator):

	bl_idname = "library.library_path"
	bl_label = "Library Path"
	
	def execute(self, context):
		filepath = context.window_manager.nexus_model_manager_dir_resource
		bpy.ops.wm.path_open(filepath=filepath)
		return {'FINISHED'}

######################################################################
############################ Asset path ############################
######################################################################

class Asset_Path(bpy.types.Operator):

	bl_idname = "library.asset_path"
	bl_label = "Library Asset Path"

	def execute(self, context):

		nexus_model_WM = bpy.data.window_managers["WinMan"].nexus_model_manager
		model_dir = context.window_manager.nexus_model_manager_dir_resource
		library = nexus_model_WM.library_list
		category = nexus_model_WM.category_list
		selected_preview = nexus_model_WM.asset_previews

		filepath = os.path.join(model_dir, library, category, selected_preview)

		bpy.ops.wm.path_open(filepath=filepath)
		return {'FINISHED'}


class NexusModelManager_WM_Properties(bpy.types.PropertyGroup):

	# scale_preview = FloatProperty(
	# 	name="Scale preview",
	# 	default=1.5,
	# 	min=1.0,
	# 	max=10.0,
	# 	soft_min=1.0,
	# 	soft_max=10.0
	# )

	link_model = BoolProperty(
		name="Link",
		description="If True link model else append model",
		default=False
	)

	instance_groups = BoolProperty(
		name="Instance groups",
		description="Instance groups",
		default=False
	)

	asset_previews = EnumProperty(
		items=enum_previews_asset_items,
	)

	library_list = EnumProperty(
		items=make_library_list,
	)

	category_list = EnumProperty(
		items=make_category_list,
	)

	group_asset = EnumProperty(
		items=enum_groups_asset
	)

	add_location = EnumProperty(
		name="Add location",
		items=[
			("CENTER", "Center", "", 0),
			("CURSOR", "Cursor", "", 1)
		],
		default = "CENTER"
	)

	add_dupligroup = BoolProperty(
		name="Add dupligroup to selected",
		description="Add dupligroup to selected objects",
		default=False
	)

######################################################################
############################## Register ##############################
######################################################################

def register():

	bpy.utils.register_class(Preferences)
	bpy.utils.register_class(Library_Path)
	# bpy.utils.register_class(AddExistGroup)
	bpy.utils.register_module(__name__)


	user_preferences = bpy.context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences

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
	pcoll.group_previews_dir = ""
	pcoll.group_previews = ()

	groups_collection["main"] = pcoll

	WindowManager.nexus_model_manager = bpy.props.PointerProperty(type=NexusModelManager_WM_Properties)


######################################################################
############################# Unregister #############################
######################################################################

def unregister():

	bpy.utils.unregister_class(Preferences)
	bpy.utils.unregister_class(Library_Path)
	# bpy.utils.unregister_class(AddExistGroup)

	del WindowManager.nexus_model_manager_dir_resource
	del WindowManager.nexus_model_manager

	for pcoll in asset_collections.values():
		bpy.utils.previews.remove(pcoll)
	asset_collections.clear()

	bpy.utils.unregister_module(__name__)



if __name__ == "__main__":
	register()
