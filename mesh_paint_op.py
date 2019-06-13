import bpy
from bpy.types import Operator

import bgl
import blf


import gpu
from gpu_extras.batch import batch_for_shader

import mathutils
import math

from mathutils import Vector, Matrix, Euler, Quaternion

import bpy_extras
from bpy_extras.view3d_utils import (
	region_2d_to_vector_3d,
	region_2d_to_origin_3d,
	location_3d_to_region_2d
)

from .functions import *

def draw_callback_3d(self, context):
	# draw brush circle
	steps = 16
	angle = (2 * math.pi) / steps
	radius = 1
	
	# calculate circle points
	rot_mat = self.normal.rotation_difference(Vector((0,0,1))).to_matrix().to_3x3()
	
	cirlce_points = []

	for i in range(steps):
		x = self.mouse_path[0].x + radius*math.cos(angle*i)
		y = self.mouse_path[0].y + radius*math.sin(angle*i)
		z = self.mouse_path[0].z
		
		p = Vector((x,y,z))
		
		# rotate circle to match the ground normal
		p -= self.mouse_path[0]
		p = p @ rot_mat
		p += self.mouse_path[0] + ( self.normal * (0.3) ) # some translate point in side normal
		cirlce_points.append(p)

	shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
	bgl.glEnable(bgl.GL_BLEND)
	bgl.glLineWidth(2)
	batch = batch_for_shader(shader, "LINE_LOOP", {"pos": cirlce_points})
	shader.bind()
	shader.uniform_float("color", (1.0, 0.0, 0.0, 1.0))
	batch.draw(shader)
		

	# shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
	# bgl.glEnable(bgl.GL_BLEND)
	bgl.glLineWidth(3)
	batch = batch_for_shader(shader, "LINE_STRIP", {"pos": self.mouse_path})
	shader.bind()
	shader.uniform_float("color", (0.0, 1.0, 1.0, 1.0))
	batch.draw(shader)

	# if self.state == "ROTATE":
	# 	arrow_rot_path = []
	# 	arrow_rot_path.append(self.new_model.location + ( self.normal * (0.3) ))
	# 	# arrow_rot_path.append(arrow_rot_path[0] + (self.rot_dir_arrow * 2))
	# 	arrow_rot_path.append(self.rot_dir_arrow)
	# 	# euler_rot = arrow_rot_path[1].to_track_quat("-Y","Z").to_euler() # -Y Z - Look At?
	# 	# arrow_rot_path[1].x = euler_rot.x
	# 	# arrow_rot_path[1].y = euler_rot.y
	# 	# arrow_rot_path[1].z = euler_rot.z

	# 	# arrow_rot_path[1].x = arrow_rot_path[0].x + radius*math.cos(math.radians(self.test_angle))
	# 	# arrow_rot_path[1].y = arrow_rot_path[0].y + radius*math.sin(math.radians(self.test_angle))
	# 	# arrow_rot_path[1].z = arrow_rot_path[0].z
	# 	# arrow_rot_path[1] = arrow_rot_path[1] @ rot_mat
		
	# 	batch = batch_for_shader(shader, "LINE_STRIP", {"pos": arrow_rot_path})
	# 	shader.bind()
	# 	shader.uniform_float("color", (0.0, 0.0, 1.0, 1.0))
	# 	batch.draw(shader)


	# restore opengl defaults
	bgl.glLineWidth(1)
	bgl.glDisable(bgl.GL_BLEND)

def draw_callback_2d(self, context):
        
	font_id = 0  # XXX, need to find out how best to get this.

	# Draw text to indicate that draw mode is active
	region = context.region
	text = "- Mesh Paint Mode -"
	subtext = "LMB - Add Model | G - Move, R - Rotate, S - Scale | RMB / ESC - Cancel"

	xt = int(region.width / 2.0)
	
	blf.size(font_id, 24, 72)
	blf.position(0, xt - blf.dimensions(0, text)[0] / 2, 60 , 0)
	blf.draw(0, text) 

	blf.size(1, 20, 72)
	blf.position(1, xt - blf.dimensions(0, subtext)[0] / 2, 30 , 1)
	blf.draw(1, subtext)

	if self.state == "ROTATE":
		line = []
		line.append((self.model_2d_point.x, self.model_2d_point.y))
		line.append((self.mouse_coord.x, self.mouse_coord.y))

		shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glLineWidth(2)
		batch = batch_for_shader(shader, "LINE_STRIP", {"pos": line})
		shader.bind()
		shader.uniform_float("color", (1.0, 1.0, 0.0, 1.0))
		batch.draw(shader)

		# restore opengl defaults
		bgl.glLineWidth(1)
		bgl.glDisable(bgl.GL_BLEND)
		


class VIEW3D_OT_MeshPaint(Operator):
	bl_idname = "viev3d.mesh_paint"
	bl_label = "Mesh Paint"


	@classmethod
	def poll(cls, context):
		return (context.mode == "OBJECT")


	def invoke(self, context, event):
		if context.area.type == "VIEW_3D":
			# the arguments we pass the the callback
			args = (self, context)
			# Add the region OpenGL drawing callback
			# draw in view space with "POST_VIEW" and "PRE_VIEW"
			self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, "WINDOW", "POST_VIEW")
			self._handle_2d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_2d, args, "WINDOW", "POST_PIXEL")

			self.state = "MOVE"

			self.mouse_path = [Vector((0, 0, 0)), Vector((0, 0, 1))]
			self.normal = Vector((0, 0, 1))

			self.rot_dir_arrow = Vector((1, 0, 0))
			self.new_scale = 1.0
			self.test_angle = 0
			self.test_angle_old = 0

			self.new_model = add_model(context, self.mouse_path[0], self.normal)

			context.window_manager.modal_handler_add(self)
			return {"RUNNING_MODAL"}
		else:
			self.report({"WARNING"}, "View3D not found, cannot run operator")
			return {"CANCELLED"}

	def get_origin_and_direction(self, event, context):
		region = context.region
		region_3d = context.space_data.region_3d

		mouse_coord = (event.mouse_region_x, event.mouse_region_y)

		origin = region_2d_to_origin_3d(region, region_3d, mouse_coord)
		direction = region_2d_to_vector_3d(region, region_3d, mouse_coord)

		return origin, direction

	def get_2d_point_from_3d(self, event, context):
		region = context.region
		region_3d = context.space_data.region_3d

		result = location_3d_to_region_2d(region, region_3d, self.new_model.location)

		return result

	def modal(self, context, event):
		context.area.tag_redraw()

		if event.type == "MOUSEMOVE":
			if self.state == "MOVE":
				# new origin and normal
				origin, direction = self.get_origin_and_direction(event, context)

				# hide mesh
				self.new_model.hide_set(True)
				# trace
				bHit, pos_hit, normal_hit, face_index_hit, obj_hit, matrix_world = context.scene.ray_cast(
					view_layer=context.view_layer,
					origin=origin,
					direction=direction
				)
				# show mesh
				self.new_model.hide_set(False)
				
				if bHit:
					self.normal = normal_hit.normalized()
					self.mouse_path[0] = pos_hit
					self.mouse_path[1] = pos_hit + (self.normal * 2.0)

					#mat_trans = Matrix.Translation(self.mouse_path[0]) # location matrix
					rot = self.normal.to_track_quat("Z","Y").to_euler()#.to_matrix().to_4x4() # rotation matrix
					self.new_model.location = self.mouse_path[0]
					self.new_model.rotation_euler = rot
					self.new_model.scale = Vector((self.new_scale, self.new_scale, self.new_scale))

					#self.new_model.matrix_world = mat_trans @ mat_rot # apply both matrix
			elif self.state == "ROTATE":
				self.model_2d_point = self.get_2d_point_from_3d(event, context)
				# self.model_2d_point = Vector((self.model_2d_point.x, self.model_2d_point.y, 0))
				self.mouse_coord = Vector((event.mouse_region_x, event.mouse_region_y))
				
				dir = self.mouse_coord - self.model_2d_point
				dir.normalize()

				self.mouse_coord = self.model_2d_point + dir * 100

				# dir = dir * 3
				# self.mouse_coord = dir

				self.test_angle = math.degrees(math.atan2(self.mouse_coord.y - self.model_2d_point.y, self.mouse_coord.x - self.model_2d_point.x))

				if self.test_angle < 0:
					self.test_angle += 360

				
				delta_angle = self.test_angle - self.test_angle_old
				self.new_model.rotation_euler.rotate_axis("Z", math.radians(delta_angle))# = Matrix.Rotation(math.radians(self.test_angle), 4, self.normal).to_euler()
				self.test_angle_old = self.test_angle
				
				# if bHit:
				# 	rot_dir = (pos_hit - self.new_model.location).normalized()
				# 	self.rot_dir_arrow = pos_hit#rot_dir
					
				
			elif self.state == "SCALE":
				pass

		if event.type == "WHEELUPMOUSE":
			self.new_scale += 0.1
			self.new_model.scale = Vector((self.new_scale, self.new_scale, self.new_scale))
			self.test_angle += 10
		elif event.type == "WHEELDOWNMOUSE":
			self.new_scale -= 0.1
			self.new_model.scale = Vector((self.new_scale, self.new_scale, self.new_scale))
			self.test_angle -= 10


		if event.value == "PRESS":
			if event.type == "R":
				self.state = "ROTATE"
				return {"RUNNING_MODAL"}

			elif event.type == "G":
				self.state = "MOVE"
				return {"RUNNING_MODAL"}

			elif event.type == "S":
				self.state = "SCALE"
				return {"RUNNING_MODAL"}

			elif event.type == "LEFTMOUSE":
				self.state = "MOVE"
				self.new_model = add_model(context, self.mouse_path[0], self.normal)
				return {"RUNNING_MODAL"}

			elif event.type in {"RIGHTMOUSE", "ESC"}:
				
				bpy.ops.object.select_all(action="DESELECT")
				self.new_model.select_set(True)
				bpy.ops.object.delete()

				bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, "WINDOW")
				bpy.types.SpaceView3D.draw_handler_remove(self._handle_2d, "WINDOW")
				return {"CANCELLED"}

		return {"RUNNING_MODAL"}
