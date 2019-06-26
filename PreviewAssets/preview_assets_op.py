import bpy
from bpy.types import Operator
from bpy.props import EnumProperty

import os

from .. enum_preview_utils import enum_previews_asset_items

class VIEW3D_OT_AddModel(Operator):
    """Add asset from library"""
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

class VIEW3D_OT_AssetPath(Operator):
	"""Open folder asset"""
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
	"""Open image preview asset"""
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
	"""Search asset by name in current category"""
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
