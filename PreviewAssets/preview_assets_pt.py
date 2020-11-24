import bpy
from bpy.types import Panel

from .. functions import get_addon_prefs

class VIEW3D_PT_ManagerPreviews(Panel):

    bl_label = "Select Asset"
    bl_idname = "VIEW3D_PT_ManagerPreviews"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Nexus"
    bl_parent_id = "VIEW3D_PT_MainPanel"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        addon_prefs = get_addon_prefs()

        nexus_model_SCN = context.scene.nexus_model_manager
        asset_name = nexus_model_SCN.asset_previews

        layout = self.layout

        ############## Panel ##############
        box = layout.box()

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
        col = box.column()
        col.scale_y = 1.5
        col.template_icon_view(nexus_model_SCN, "asset_previews", show_labels=True, scale_popup=addon_prefs.preview_asset_scale)
        # col.template_ID_preview(asset_collections["main"].asset_previews, "name", rows=3, cols=8)
        # col.template_search_preview(nexus_model_SCN, "asset_previews", search_data, "name")
        col.label(text=asset_name)

        row = box.row()
        row.operator("view3d.search_asset", icon="VIEWZOOM", text="Search Asset")

        col = box.column()
        col.scale_y = 1.5
        col.template_icon_view(nexus_model_SCN, "collection_previews", show_labels=True, scale_popup=addon_prefs.preview_asset_scale)

        ######### Add location
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
        col.operator("view3d.add_model", icon="ADD", text="Add Asset")
