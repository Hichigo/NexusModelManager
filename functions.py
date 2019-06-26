import bpy
import os
import math
from random import randint

from mathutils import Vector, Matrix, Euler

def filter_on_mesh_prop(self, object):
    return object.type == "MESH"

def get_addon_prefs():
    addon_name = __name__.split(".")[0]
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return addon_prefs

def get_addon_dir():
    path = os.path.realpath(__file__)
    path = os.path.dirname(path)
    return path

def add_model(context, location, normal):
    nexus_model_SCN = context.scene.nexus_model_manager

    filepath_collection_name = None
    asset_name = None
    directory_inside_file = None

    random_asset_not_empty = len(context.scene.random_asset_list.list_item)

    if nexus_model_SCN.use_random_asset and random_asset_not_empty:
        random_asset_list = context.scene.random_asset_list
        number_assets = len(random_asset_list.list_item) - 1

        index_asset = randint(0, number_assets)

        filepath = random_asset_list.list_item[index_asset].path_to_asset
        directory_inside_file = os.path.join(filepath, "Collection")

        asset_name = random_asset_list.list_item[index_asset].name

        filepath_collection_name = directory_inside_file + asset_name
    
    else:
        path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
        asset_name = nexus_model_SCN.asset_previews
        category = nexus_model_SCN.category_list
        library = nexus_model_SCN.library_list

        filepath = os.path.join(path_models, library, category, asset_name, asset_name + ".blend")

        directory_inside_file = os.path.join(filepath, "Collection")

        filepath_collection_name = directory_inside_file + asset_name

        bpy.ops.object.select_all(action="DESELECT")

    bpy.ops.wm.link(
        filepath=filepath_collection_name,
        filename=asset_name,
        directory=directory_inside_file,
        link=True,
        instance_collections=True,
        autoselect=True
    )

    mat_trans = Matrix.Translation(location) # location matrix
    mat_rot = normal.to_track_quat("Z","Y").to_matrix().to_4x4() # rotation matrix
    context.selected_objects[0].matrix_world = mat_trans @ mat_rot # apply both matrix
    
    return context.selected_objects[0]