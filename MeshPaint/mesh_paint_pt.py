import bpy
from bpy.types import Panel

class VIEW3D_PT_MeshPaint(Panel):
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
		random_asset_list = context.scene.random_asset_list
		
		layout.prop(nexus_model_SCN, "align_by_normal")
		layout.operator("viev3d.mesh_paint", text="Place Asset", icon="SCENE_DATA")
		layout.prop(nexus_model_SCN, "distance_between_asset")
		layout.prop_search(nexus_model_SCN, "canvas_object", context.scene, "objects")

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

		box = layout.box()
		box.label(text="Random assets")
		col = box.column(align=True)
		col.prop(nexus_model_SCN, "use_random_asset")
		if nexus_model_SCN.use_random_asset:
			col.template_list("STRING_UL_RandomAssets", "random_assets", random_asset_list, "list_item", random_asset_list, "active_index")
			col = box.column()
			row = col.row(align=True)
			row.operator("scene.add_list_item", icon="ADD")
			row.operator("scene.remove_list_item", icon="REMOVE")