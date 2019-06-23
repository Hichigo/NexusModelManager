import bpy

class STRING_UL_RandomAssets(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        name = item.name

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=name, icon_value=icon)
            # layout.prop(item, "path_to_asset", text="")
        # elif self.layout_type in {'GRID'}:
        #     layout.alignment = 'CENTER'
        #     layout.label(text="", icon_value=icon)