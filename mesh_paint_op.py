import bpy
from bpy.types import Operator

import bgl
import blf


import gpu
from gpu_extras.batch import batch_for_shader

# import mathutils
# import math

from mathutils import Vector

from bpy_extras.view3d_utils import (
	region_2d_to_vector_3d,
	region_2d_to_origin_3d
)

def draw_callback_px(self, context):
	font_id = 0  # XXX, need to find out how best to get this.

	# draw some text
	blf.position(font_id, 15, 30, 0)
	blf.size(font_id, 20, 72)
	blf.draw(font_id, "LMB - Add Mesh | RMB / ESC - Exit")

	# 50% alpha, 2 pixel width line
	shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
	bgl.glEnable(bgl.GL_BLEND)
	bgl.glLineWidth(3)
	batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": self.mouse_path})
	shader.bind()
	shader.uniform_float("color", (0.0, 0.0, 1.0, 1.0))
	batch.draw(shader)

	# restore opengl defaults
	bgl.glLineWidth(1)
	bgl.glDisable(bgl.GL_BLEND)


class MeshPaint_OT_Operator(Operator):
	bl_idname = "viev3d.mesh_paint"
	bl_label = "Mesh Paint"


	@classmethod
	def poll(cls, context):
		return (context.mode == "OBJECT")


	def invoke(self, context, event):
		if context.area.type == 'VIEW_3D':
			# the arguments we pass the the callback
			args = (self, context)
			# Add the region OpenGL drawing callback
			# draw in view space with 'POST_VIEW' and 'PRE_VIEW'
			self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_VIEW')

			self.mouse_path = [(), ()]

			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "View3D not found, cannot run operator")
			return {'CANCELLED'}

	def get_origin_and_direction(self, event, context):
		region = context.region
		region_3d = context.space_data.region_3d

		mouse_coord = (event.mouse_region_x, event.mouse_region_y)

		origin = region_2d_to_origin_3d(region, region_3d, mouse_coord)
		direction = region_2d_to_vector_3d(region, region_3d, mouse_coord)

		return origin, direction

	def modal(self, context, event):
		context.area.tag_redraw()

		if event.type == 'MOUSEMOVE':
			# new origin and normal
			origin, direction = self.get_origin_and_direction(event, context)

			bHit, pos_hit, normal_hit, face_index_hit, obj_hit, matrix_world = context.scene.ray_cast(
				view_layer=context.view_layer,
				origin=origin,
				direction=direction
			)
			
			if bHit:
				self.mouse_path[0] = pos_hit
				self.mouse_path[1] = pos_hit + (normal_hit * 2.0)


		elif event.type == 'LEFTMOUSE':
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			return {'FINISHED'}

		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}
