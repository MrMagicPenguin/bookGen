import bpy
from mathutils import Vector, Matrix
import random
import logging
import time
from math import pi, radians, sin, cos, tan, asin, degrees, sqrt

from .shelf import Shelf
from .utils import (visible_objects_and_instances,
                   obj_ray_cast,
                   get_bookgen_collection,
                   get_shelf_parameters,
                   get_shelf_collection,
                   get_click_position_on_object)


class OBJECT_OT_BookGenRebuild(bpy.types.Operator):
    bl_idname = "object.book_gen_rebuild"
    bl_label = "BookGen"
    bl_options = {'REGISTER'}

    """def hinge_inset_guard(self, context):
        if(self.hinge_inset > self.cover_thickness):
            self.hinge_inset = self.cover_thickness - self.cover_thickness / 8"""

    log = logging.getLogger("bookGen.operator")

    def check(self, context):
        self.run()

    def invoke(self, context, event):
        self.run()
        return {'FINISHED'}

    def execute(self, context):
        self.run()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def run(self):

        time_start = time.time()
        parameters = get_shelf_parameters()

        for shelf_collection in get_bookgen_collection().children:
            shelf_props = shelf_collection.BookGenShelfProperties

            parameters["seed"] += shelf_props.id

            shelf = Shelf(shelf_collection.name, shelf_props.start, shelf_props.end, shelf_props.normal, parameters)
            shelf.clean()
            shelf.fill()

            parameters["seed"] -= shelf_props.id

        self.log.info("Finished populating shelf in %.4f secs" % (time.time() - time_start))


class BookGen_SelectShelf(bpy.types.Operator):
    bl_idname = "object.book_gen_select_shelf"
    bl_label = "Select BookGen Shelf"
    log = logging.getLogger("bookGen.select_shelf")

    def modal(self, context, event):
        context.area.header_text_set("Left click on a surface to place your shelf.")
        x, y = event.mouse_region_x, event.mouse_region_y
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self.start is None:
                self.start, self.start_normal = get_click_position_on_object(x, y)
                return { 'RUNNING_MODAL' }
            else:
                self.end, self.end_normal = get_click_position_on_object(x, y)
                shelf_id = len(get_bookgen_collection().children)
                parameters = get_shelf_parameters()
                parameters["seed"] += shelf_id
                normal = (self.start_normal  + self.end_normal)/2
                shelf = Shelf("shelf_"+str(shelf_id), self.start, self.end, normal, parameters)
                shelf.clean()
                shelf.fill()
                
                # set properties for later rebuild
                shelf_props = get_shelf_collection(shelf.name).BookGenShelfProperties
                shelf_props.start = self.start
                shelf_props.end = self.end
                shelf_props.normal = normal
                shelf_props.id = shelf_id
                context.area.header_text_set("")
                return { 'FINISHED' }
        elif event.type in { 'RIGHTMOUSE', 'ESC' }:
            context.area.header_text_set("")
            return { 'CANCELLED' }
        return { 'RUNNING_MODAL' }

    def invoke(self, context, event):

        self.start = None
        self.end = None

        context.window_manager.modal_handler_add(self)
        return { 'RUNNING_MODAL' }
