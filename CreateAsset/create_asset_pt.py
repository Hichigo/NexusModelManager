import bpy
from bpy.types import Panel

from .. functions import get_addon_prefs

class VIEW3D_PT_CreateAsset(Panel):
    """Create .blend file and render icon"""
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
        addon_prefs = get_addon_prefs()
        layout = self.layout
        nexus_model_SCN = context.scene.nexus_model_manager

        col = layout.column(align=True)
        row = col.row()
        row.prop(nexus_model_SCN, "library_list", text="Library", icon="FILE_FOLDER")
        row.operator("view3d.add_folder", text="", icon="NEWFOLDER").folder_place = "LIBRARY"
        # row.operator("view3d.remove_folder", text="", icon="TRASH").folder_place = "LIBRARY"

        col = layout.column(align=True)
        row = col.row()
        row.prop(nexus_model_SCN, "category_list", text="Category", icon="FILE_FOLDER")
        row.operator("view3d.add_folder", text="", icon="NEWFOLDER").folder_place = "CATEGORY"
        # row.operator("view3d.remove_folder", text="", icon="TRASH").folder_place = "CATEGORY"

        col = layout.column(align=True)
        col.prop(nexus_model_SCN, "new_collection_name")
        col.operator("view3d.create_asset_path", text="Create Asset", icon="FILE_NEW")

        box = layout.box()

        box.label(text="Settings")
        box.prop(nexus_model_SCN, "apply_cursor_rotation")

        box.prop(nexus_model_SCN, "pack_data", text="Pack data")

        col = box.column()
        col.label(text="Render Scene")
        col.scale_y = 1.5
        col.template_icon_view(nexus_model_SCN, "render_scenes", show_labels=True, scale_popup=addon_prefs.preview_asset_scale)