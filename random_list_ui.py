import bpy
from bpy.props import *

class STRING_UL_RandomAssets(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        name = item.name

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=name, icon_value=icon)
            # layout.prop(item, "path_to_asset", text="")
        # elif self.layout_type in {'GRID'}:
        #     layout.alignment = 'CENTER'
        #     layout.label(text="", icon_value=icon)

class ListItem(bpy.types.PropertyGroup):
	# name_asset: StringProperty(name="Name", default="Empty")
	path_to_asset: StringProperty(name="Name", default="")

class UIList_WM_Properties(bpy.types.PropertyGroup):
    list_item: CollectionProperty(name="List item", type=ListItem)
    active_index: IntProperty(name="Active Index", default=-1)