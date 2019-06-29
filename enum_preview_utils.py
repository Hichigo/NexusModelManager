import bpy
import os
import glob

from .functions import get_addon_dir, get_addon_prefs

def make_library_list_folders(self, context):
	addon_prefs = get_addon_prefs()

	items = []
	i = 0
	for lib in addon_prefs.library_folders:
		items.append((lib.path_to_folder, lib.name, "", i))
		i += 1

	if len(items) == 0:
		addon_folder = get_addon_dir()
		default_library_path = os.path.join(addon_folder, "resources", "LibraryModels")
		items.append((default_library_path, "Default Library", "", 0))

	items.sort()

	return items

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
	addon_prefs = get_addon_prefs()
	library_dir = addon_prefs.library_list
	library = context.scene.nexus_model_manager.library_list
	path_category = os.path.join(library_dir, library)

	return make_list_folder(path_category)

############################ Library ##########################
def make_library_list(self, context):
	addon_prefs = get_addon_prefs()
	library_dir = addon_prefs.library_list

	return make_list_folder(library_dir)

######### Assets Previews ##########
def enum_previews_asset_items(self, context):
	""" create assets items prewiews """
	enum_items = []

	addon_prefs = get_addon_prefs()
	library_dir = addon_prefs.library_list
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