import bpy
import os
import math

from mathutils import Vector, Matrix, Euler


def add_model(context, location, normal):
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


    #selected_objects = context.selected_objects

    #if not add_dupli_to_sel:
    bpy.ops.object.select_all(action='DESELECT')

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
    
    # context.selected_objects[0].location = location
    mat_trans = Matrix.Translation(location)
    

    #euler_rotation = Euler(normal, 'XYZ').to_matrix().to_4x4()

    #rot = normal.to_track_quat("X", "Z").to_euler().to_matrix().to_4x4()
    rot = normal.rotation_difference(Vector((0,0,1))).to_matrix().to_4x4()

    context.selected_objects[0].matrix_world = mat_trans @ rot#euler_rotation
    print(normal)
    print(rot)


    # // Find yaw. z
	# R.Yaw = FMath::Atan2(Y,X) * (180.f / PI);
    # yaw = math.atan2(normal.y, normal.x) * (180.0 / math.pi)

	# // Find pitch. y
	# R.Pitch = FMath::Atan2(Z,FMath::Sqrt(X*X+Y*Y)) * (180.f / PI);
    # pitch = math.atan2(normal.z, math.sqrt(normal.x*normal.x+normal.y*normal.y)) * (180.0 / math.pi)

	# // Find roll.
	# R.Roll = 0; x
    # roll = 0

    # context.selected_objects[0].rotation_euler.x = roll # = normal.to_track_quat('X', 'Z').to_euler()
    # context.selected_objects[0].rotation_euler.y = pitch
    # context.selected_objects[0].rotation_euler.z = yaw

    # mw = context.selected_objects[0].matrix_world.copy()

    # matrix_translation = Matrix.Translation(mw @ location)

    
    # matrix_rotate = mw.to_3x3()
    # matrix_rotate = matrix_rotate @ normal.rotation_difference(Vector((0,0,1))).to_matrix()
    # context.selected_objects[0].matrix_world = matrix_translation @ matrix_rotate.to_4x4()
    
    
