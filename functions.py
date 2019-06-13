import bpy
import os
import math

from mathutils import Vector, Matrix, Euler

def get_file_dir(file):
    path = os.path.realpath(file)
    path = os.path.dirname(path)
    return path

def add_model(context, location, normal):
    nexus_model_SCN = context.scene.nexus_model_manager
    path_models = bpy.data.window_managers["WinMan"].nexus_model_manager_dir_resource
    filename = nexus_model_SCN.asset_previews
    category = nexus_model_SCN.category_list
    library = nexus_model_SCN.library_list
    collection_name = nexus_model_SCN.collection_asset
    collection_or_meshdata = nexus_model_SCN.collection_or_meshdata

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

    bpy.ops.object.select_all(action="DESELECT")

    bpy.ops.wm.link(
        filepath=filepath_collection_name,
        filename=collection_name,
        directory=directory_inside_file,
        link=True,
        instance_collections=True,
        autoselect=True
    )
    
    mat_trans = Matrix.Translation(location) # location matrix
    mat_rot = normal.to_track_quat("Z","Y").to_matrix().to_4x4() # rotation matrix
    context.selected_objects[0].matrix_world = mat_trans @ mat_rot # apply both matrix
    return context.selected_objects[0]
