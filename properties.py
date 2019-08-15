import bpy
from bpy.props import *
from bpy.types import PropertyGroup

from .functions import filter_on_mesh_prop
from .enum_preview_utils import *

class NexusModelManager_WM_Properties(PropertyGroup):

	canvas_object: PointerProperty(
		name="Canvas",
		description="If empty then will draw over all objects. APPLY TRANSFORM TO OBJECT!!!",
        type=bpy.types.Object,
        poll=filter_on_mesh_prop
    )

	new_library_name: StringProperty(
		name="Library",
		description="Name of New Library",
		default="Awesome_Library"
	)

	new_category_name: StringProperty(
		name="Category",
		description="Name of New Category",
		default="Awesome_Category"
	)

	new_collection_name: StringProperty(
		name="Collection",
		description="Name of New Collection",
		default="Awesome_Collection"
	)

	align_by_normal: BoolProperty(
		name="Align by Normal",
		description="Align asset by normal",
		default=True
	)

	apply_cursor_rotation: BoolProperty(
		name="Apply 3D Cursor Rotation",
		description="Apply 3D Cursor Rotation to New Asset",
		default=True
	)

	link_model: BoolProperty(
		name="Link",
		description="If True link model else append model",
		default=True
	)

	set_to_selected_objects: BoolProperty(
		name="Set to selected objects",
		description="Set mesh data to selected objects",
		default=False
	)

	distance_between_asset: FloatProperty(
		name="Distance",
		description="Distance to which assets can be placed",
		min=0,
		default=2
	)

	use_random_asset: BoolProperty(
		name="Use random asset",
		description="If True get asset from list",
		default=False
	)

	use_random_rotation: BoolProperty(
		name="Use random rotation",
		description="Set random rotation to asset",
		default=False
	)

	random_rotation_x: FloatProperty(
		name="X",
		description="Random rotation by X",
		min=0,
		max=359,
		default=0
	)
	random_rotation_y: FloatProperty(
		name="Y",
		description="Random rotation by Y",
		min=0,
		max=359,
		default=0
	)
	random_rotation_z: FloatProperty(
		name="Z",
		description="Random rotation by Z",
		min=0,
		max=359,
		default=0
	)

	use_random_scale: BoolProperty(
		name="Use random scale",
		description="Set random scale to asset",
		default=False
	)
	random_scale_from: FloatProperty(
		name="From",
		description="Random scale from",
		min=0,
		default=1
	)
	random_scale_to: FloatProperty(
		name="To",
		description="Random scale to",
		min=0,
		default=2
	)

	asset_previews: EnumProperty(
		items=enum_previews_asset_items
	)

	library_list: EnumProperty(
		items=make_library_list
	)

	category_list: EnumProperty(
		items=make_category_list
	)

	render_scenes: EnumProperty(
		items=enum_render_scenes
	)

	pack_data: EnumProperty(
		name="Pack data",
		items=[
			("NONE", "None", "", 0),
			("PACK", "Pack to .blend", "", 1),
			("TEXTURE", "Texture to library", "", 2)
		],
		default = "NONE"
	)

	add_location: EnumProperty(
		name="Add location",
		items=[
			("CENTER", "Center", "", 0),
			("CURSOR", "Cursor", "", 1)
		],
		default = "CENTER"
	)

	add_duplicollection: BoolProperty(
		name="Add duplicollection to selected",
		description="Add duplicollection to selected objects",
		default=False
	)