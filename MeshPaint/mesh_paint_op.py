import bpy
from bpy.types import Operator
from bpy.props import EnumProperty

import bgl
import blf

import os

import gpu
from gpu_extras.batch import batch_for_shader

import mathutils
import math
from random import uniform

from mathutils import Vector, Matrix, Euler, Quaternion

import bpy_extras
from bpy_extras.view3d_utils import (
	region_2d_to_vector_3d,
	region_2d_to_origin_3d,
	location_3d_to_region_2d
)

from .. functions import *
from .. enum_preview_utils import enum_previews_asset_items

def draw_callback_3d(self, context):
	nexus_model_SCN = context.scene.nexus_model_manager
	align_by_normal = nexus_model_SCN.align_by_normal
	# draw brush circle
	steps = 16
	angle = (2 * math.pi) / steps
	radius = nexus_model_SCN.distance_between_asset
	
	# calculate circle points
	rot_mat = self.normal.rotation_difference(Vector((0,0,1))).to_matrix().to_3x3()
	
	cirlce_points = []

	for i in range(steps):
		x = self.mouse_path[0].x + radius*math.cos(angle*i)
		y = self.mouse_path[0].y + radius*math.sin(angle*i)
		z = self.mouse_path[0].z
		
		p = Vector((x,y,z))
		
		# rotate circle to match the ground normal
		if align_by_normal:
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

	# if self.transform_mode == "ROTATE":
	# 	arrow_rot_path = []
	# 	arrow_rot_path.append(self.current_model.location + ( self.normal * (0.3) ))
	# 	# arrow_rot_path.append(arrow_rot_path[0] + (self.rot_dir_arrow * 2))
	# 	arrow_rot_path.append(self.rot_dir_arrow)
	# 	# euler_rot = arrow_rot_path[1].to_track_quat("-Y","Z").to_euler() # -Y Z - Look At?
	# 	# arrow_rot_path[1].x = euler_rot.x
	# 	# arrow_rot_path[1].y = euler_rot.y
	# 	# arrow_rot_path[1].z = euler_rot.z

	# 	# arrow_rot_path[1].x = arrow_rot_path[0].x + radius*math.cos(math.radians(self.rotate_angle))
	# 	# arrow_rot_path[1].y = arrow_rot_path[0].y + radius*math.sin(math.radians(self.rotate_angle))
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
	# subtext = "LMB - Add Model | G - Move, R - Rotate, MOUSEWHEEL 0.1, 0.01 (shift) - Scale | RMB / ESC - Cancel"

	xt = int(region.width / 2.0)
	
	blf.size(font_id, 24, 72)
	blf.position(0, xt - blf.dimensions(0, text)[0] / 2, 60 , 0)
	blf.draw(0, text) 

	# blf.size(font_id, 20, 72)
	# blf.position(1, xt - blf.dimensions(0, subtext)[0] / 2, 30 , 1)
	# blf.draw(1, subtext)

	if self.transform_mode == "ROTATE":
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

		text_angle = "{}".format(round(self.rotate_angle, 2))
		blf.size(font_id, 20, 72)
		blf.position(2, line[0][0], line[0][1]+100, 1)
		blf.draw(2, text_angle)

		# restore opengl defaults
		bgl.glLineWidth(1)
		bgl.glDisable(bgl.GL_BLEND)
		
def random_scale_and_rotation(obj, normal, NM_SCN, self_data):
	loc, rot, scale = obj.matrix_world.decompose()

	loc = Matrix.Translation(loc)
	rot = rot.to_euler().to_matrix().to_4x4()

	rot_add = Euler( Vector( (0, 0, math.radians(self_data.rotate_angle) ) ) )
	rot_add = rot_add.to_matrix().to_4x4()



	if NM_SCN.use_random_scale:
		new_scale = uniform(NM_SCN.random_scale_from, NM_SCN.random_scale_to)
		scale = Matrix.Scale(new_scale, 4)
	else:
		scale = Matrix.Scale(self_data.scale_model, 4)

	# apply rotation by normal if checked "align_by_normal"
	if NM_SCN.align_by_normal:
		rot_by_normal = normal.rotation_difference(Vector((0,0,1)))
		rot_by_normal.invert()
		rot_by_normal = rot_by_normal.to_euler().to_matrix().to_4x4()
		rot = rot_by_normal @ rot_add
	else:
		rot = Euler((0,0,0)).to_matrix().to_4x4()
		rot = rot @ rot_add
	
	if NM_SCN.use_random_rotation:
		x_angle = math.radians(uniform(0, NM_SCN.random_rotation_x))
		y_angle = math.radians(uniform(0, NM_SCN.random_rotation_y))
		z_angle = math.radians(uniform(0, NM_SCN.random_rotation_z))

		rot_rand = Euler( Vector( (x_angle, y_angle, z_angle ) ) ).to_matrix().to_4x4()
		rot = rot @ rot_rand

	mat_w = loc @ rot @ scale

	obj.matrix_world = mat_w

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

			self.transform_mode = "MOVE"

			self.mouse_path = [Vector((0, 0, 0)), Vector((0, 0, 1))]
			self.normal = Vector((0, 0, 1))

			self.rot_dir_arrow = Vector((1, 0, 0))
			self.scale_model = 1.0
			self.rotate_angle = 0
			self.rotate_angle_old = 0

			self.model_2d_point = None

			self.LMB_PRESS = False
			# self.draw_mouse_path = [] # 2d path screen space
			self.prev_location = None

			# self.start_distance_scale = 0
			# self.current_distance_scale = 0

			self.current_model = add_model(context, self.mouse_path[0], self.normal, self.scale_model)

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

		result = location_3d_to_region_2d(region, region_3d, self.current_model.location)

		return result
	
	def calculate_angle(self, event, context):
		self.model_2d_point = self.get_2d_point_from_3d(event, context)
		self.mouse_coord = Vector((event.mouse_region_x, event.mouse_region_y))

		dir = self.mouse_coord - self.model_2d_point
		dir.normalize()

		self.mouse_coord = self.model_2d_point + dir * 100

		self.rotate_angle = math.degrees(math.atan2(self.mouse_coord.y - self.model_2d_point.y, self.mouse_coord.x - self.model_2d_point.x))

		if self.rotate_angle < 0:
			self.rotate_angle += 360

	def change_scale_current_model(self, context, event):
		loc, rot, scale = self.current_model.matrix_world.decompose()

		loc = Matrix.Translation(self.mouse_path[0])
		rot = rot.to_matrix().to_4x4()
		scale = Matrix.Scale(self.scale_model, 4)

		mat_w = loc @ rot @ scale
		self.current_model.matrix_world = mat_w
	
	def draw_asset(self, context, event):
		if self.LMB_PRESS:
			nexus_model_SCN = context.scene.nexus_model_manager
			# self.draw_mouse_path.append((event.mouse_region_x, event.mouse_region_y)) # 2d path screen space
			distance = 0
			distance_vector = Vector(
				(
					self.prev_location.x - self.current_model.location.x,
					self.prev_location.y - self.current_model.location.y,
					self.prev_location.z - self.current_model.location.z
				)
			)

			distance = distance_vector.length

			# for point in self.draw_mouse_path:
			# 	if old_point != None:
			# 		distance += math.hypot(old_point[0] - point[0], old_point[1] - point[1])
			# 	# else:
			# 	# 	distance += math.hypot(point[0], point[1])
			
			# 	old_point = point

			if distance >= nexus_model_SCN.distance_between_asset:
				# self.draw_mouse_path = []
				# self.draw_mouse_path.append((event.mouse_region_x, event.mouse_region_y))
				self.prev_location = self.current_model.location
				distance = 0
				
				random_scale_and_rotation(self.current_model, self.normal, nexus_model_SCN, self)

				self.current_model = add_model(context, self.mouse_path[0], self.normal, self.scale_model)

	def modal(self, context, event):
		context.area.tag_redraw()
		nexus_model_SCN = context.scene.nexus_model_manager
		mod = None
		if event.shift:
			mod = "SHIFT"
        # if event.alt:
        #     mod.append("Alt")
        # if event.ctrl:
        #     mod.append("Ctrl")
		tip_text = "LMB - Add Model | G - Move, R - Rotate, MOUSEWHEEL 0.1, +shift 0.01 - Scale | N - Align by normal | RMB / ESC - Cancel"
		context.area.header_text_set(tip_text)

		if event.type == "MOUSEMOVE":
			if self.transform_mode == "MOVE":
				# new origin and normal
				origin, direction = self.get_origin_and_direction(event, context)


				bHit = None
				pos_hit = None
				normal_hit = None
				face_index_hit = None
				obj_hit = None
				matrix_world = None

				# hide mesh
				self.current_model.hide_set(True)

				canvas = nexus_model_SCN.canvas_object
				if canvas == None:
					# trace
					bHit, pos_hit, normal_hit, face_index_hit, obj_hit, matrix_world = context.scene.ray_cast(
						view_layer=context.view_layer,
						origin=origin,
						direction=direction
					)
				else:
					# trace
					bHit, pos_hit, normal_hit, face_index_hit = canvas.ray_cast(
						origin=origin,
						direction=direction
					)

				# show mesh
				self.current_model.hide_set(False)
				
				if bHit:
					self.normal = normal_hit.normalized()
					self.mouse_path[0] = pos_hit
					self.mouse_path[1] = pos_hit + (self.normal * 2.0)

					loc, rot, scale = self.current_model.matrix_world.decompose()

					loc = Matrix.Translation(self.mouse_path[0])

					rot_add = Euler( Vector( (0, 0, math.radians(self.rotate_angle) ) ) )
					rot_add = rot_add.to_matrix().to_4x4()

					scale = Matrix.Scale(self.scale_model, 4)

					# apply rotation by normal if checked "align_by_normal"
					if nexus_model_SCN.align_by_normal:
						# rot = self.normal.to_track_quat("Z","Y").to_euler()
						rot = self.normal.rotation_difference(Vector((0,0,1)))
						rot.invert()
						rot = rot.to_euler().to_matrix().to_4x4()
					else:
						rot = Euler((0,0,0)).to_matrix().to_4x4()
					
					rot = rot @ rot_add
					mat_w = loc @ rot @ scale

					self.current_model.matrix_world = mat_w

					# draw assets
					self.draw_asset(context, event)

			elif self.transform_mode == "ROTATE":
				self.calculate_angle(event, context)

				delta_angle = self.rotate_angle - self.rotate_angle_old
				self.current_model.rotation_euler.rotate_axis("Z", math.radians(delta_angle))
				self.rotate_angle_old = self.rotate_angle
				
			# elif self.transform_mode == "SCALE":
				# self.model_2d_point = self.get_2d_point_from_3d(event, context)
				# x = self.model_2d_point.x - event.mouse_region_x
				# y = self.model_2d_point.y - event.mouse_region_y
				# self.current_distance_scale = math.hypot(x, y)
				# delta_scale = self.current_distance_scale - self.start_distance_scale
				# self.scale_model = self.scale_model + delta_scale * 0.1
				# self.current_model.scale = Vector((self.scale_model, self.scale_model, self.scale_model))

		if event.type == "WHEELUPMOUSE":
			if mod != "SHIFT":
				self.scale_model += 0.1
			else:
				self.scale_model += 0.01
			self.change_scale_current_model(context, event)
		elif event.type == "WHEELDOWNMOUSE":
			if mod != "SHIFT":
				self.scale_model -= 0.1
			else:
				self.scale_model -= 0.01
			self.change_scale_current_model(context, event)

		if event.value == "PRESS":
			if event.type == "LEFTMOUSE":
				self.transform_mode = "MOVE"
				self.LMB_PRESS = True
				# self.draw_mouse_path.append((event.mouse_region_x, event.mouse_region_y)) # 2d path screen space
				random_scale_and_rotation(self.current_model, self.normal, nexus_model_SCN, self)
				self.prev_location = self.current_model.location # 3d path world path
				self.current_model = add_model(context, self.mouse_path[0], self.normal, self.scale_model)
				return {"RUNNING_MODAL"}
			elif event.type == "R":
				self.transform_mode = "ROTATE"
				return {"RUNNING_MODAL"}
			elif event.type == "G":
				self.transform_mode = "MOVE"
				return {"RUNNING_MODAL"}
			# elif event.type == "S":
			# 	self.transform_mode = "SCALE"
			# 	self.model_2d_point = self.get_2d_point_from_3d(event, context)
			# 	x = self.model_2d_point.x - event.mouse_region_x
			# 	y = self.model_2d_point.y - event.mouse_region_y
			# 	self.start_distance_scale = math.hypot(x, y)	
			# 	return {"RUNNING_MODAL"}
			elif event.type == "N":
				nexus_model_SCN.align_by_normal = not nexus_model_SCN.align_by_normal
				return {"RUNNING_MODAL"}
			elif event.type in {"RIGHTMOUSE", "ESC"}:
				
				bpy.ops.object.select_all(action="DESELECT")
				self.current_model.select_set(True)
				bpy.ops.object.delete()

				bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, "WINDOW")
				bpy.types.SpaceView3D.draw_handler_remove(self._handle_2d, "WINDOW")
				context.area.header_text_set(text=None) # return header text to default
				return {"CANCELLED"}

		if event.value == "RELEASE":
			if event.type == "LEFTMOUSE":
				self.LMB_PRESS = False
				# self.draw_mouse_path = [] # 2d path screen space

		return {"RUNNING_MODAL"}

class SCENE_OT_AddListItem(Operator):
	bl_idname = "scene.add_list_item"
	bl_label = "Add Item"
	bl_property = "search_asset"

	search_asset: EnumProperty(
		name="Search Asset",
		items=enum_previews_asset_items,
	)

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {"RUNNING_MODAL"}

	def execute(self, context):
		random_asset_list = context.scene.random_asset_list
		new_index = len(random_asset_list.list_item)
		asset_name = self.search_asset
		if new_index > 0: # if list items not empty, check item exists
			if random_asset_list.list_item.find(asset_name) != -1:
				self.report({"INFO"}, "This asset exists in list!")
				return {"CANCELLED"}

		# create new item
		random_asset_list.list_item.add()
		
		# set item name
		random_asset_list.list_item[new_index].name = asset_name

		# make path to asset
		nexus_model_SCN = context.scene.nexus_model_manager
		addon_prefs = get_addon_prefs()
		library_dir = addon_prefs.library_list
		
		library = nexus_model_SCN.library_list
		category = nexus_model_SCN.category_list

		filepath_to_asset = os.path.join(library_dir, library, category, asset_name, asset_name + ".blend")

		# set filepath to asset
		random_asset_list.list_item[new_index].path_to_asset = filepath_to_asset

		# set active index
		random_asset_list.active_index = new_index
		
		return {'FINISHED'}

class SCENE_OT_RemoveListItem(Operator):
	bl_idname = "scene.remove_list_item"
	bl_label = "Remove Item"

	def execute(self, context):
		random_asset_list = context.scene.random_asset_list
		remove_index = random_asset_list.active_index
		
		# remove item
		random_asset_list.list_item.remove(remove_index)

		return {'FINISHED'}
