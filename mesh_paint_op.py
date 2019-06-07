import bpy
from bpy.types import Operator

import bgl
import blf


import gpu
from gpu_extras.batch import batch_for_shader

import mathutils
import math

from mathutils import Vector

from bpy_extras.view3d_utils import (
    region_2d_to_vector_3d,
    region_2d_to_origin_3d
)


class MeshPaint_OT_Operator(bpy.types.Operator):
    bl_idname = "object.mesh_paint"
    bl_label = "Mesh Paint"

    def execute(self, context):
        return {'FINISHED'}
