import bpy
from bpy.props import FloatProperty, IntProperty, EnumProperty, BoolProperty, FloatVectorProperty, PointerProperty

from .utils import get_bookgen_collection
from .ui_outline import BookGenShelfOutline

from math import pi, radians
import logging


class BookGenShelfProperties(bpy.types.PropertyGroup):
    start: FloatVectorProperty(name="start")
    end: FloatVectorProperty(name="end")
    normal: FloatVectorProperty(name="normal")
    id: IntProperty(name="id")

class BookGenProperties(bpy.types.PropertyGroup):
    log = logging.getLogger("bookGen.properties")
    outline = BookGenShelfOutline()
    
    def update(self, context):
        properties = get_bookgen_collection().BookGenProperties
        self.log.debug("auto rebuild: %r" % properties.auto_rebuild)
        if properties.auto_rebuild:
            bpy.ops.object.book_gen_rebuild()

    def update_outline_active(self, context):
        properties = get_bookgen_collection().BookGenProperties
        if properties.outline_active:
            self.outline.enable_outline(properties.active_shelf, context)
        else:
            self.outline.disable_outline()

    def update_active_shelf(self, context):
        properties = get_bookgen_collection().BookGenProperties
        self.outline.update(properties.active_shelf, context)

    # general
    auto_rebuild: BoolProperty(name="auto rebuild", default=True)
    active_shelf: IntProperty(name="active_shelf", update=update_active_shelf)
    outline_active: BoolProperty(name="outline active shelf", default=False, update=update_outline_active)

    #shelf
    scale: FloatProperty(name="scale", min=0.1, default=1,  update=update)

    seed: IntProperty(name="seed", default=0, update=update)

    alignment:  EnumProperty(name="alignment", items=(("0", "fore edge", "align books at the fore edge"), (
        "1", "spine", "align books at the spine"), ("2", "center", "align at center")), update=update)

    lean_amount:  FloatProperty(
        name="lean amount", subtype="FACTOR", min=.0, soft_max=1.0, update=update)

    lean_direction: FloatProperty(
        name="lean direction", subtype="FACTOR", min=-1, max=1, default=0, update=update)

    lean_angle: FloatProperty(
        name="lean angle", unit='ROTATION', min=.0, soft_max=radians(30), max=pi / 2.0, default=radians(8), update=update)
    rndm_lean_angle_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    book_height: FloatProperty(
        name="height", default=0.15, min=.0, unit="LENGTH", update=update)
    rndm_book_height_factor: FloatProperty(
        name=" random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    book_width: FloatProperty(
        name="width", default=0.03, min=.002, step=0.005, unit="LENGTH", update=update)
    rndm_book_width_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    book_depth: FloatProperty(
        name="depth", default=0.12, min=.0, unit="LENGTH", update=update)
    rndm_book_depth_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    cover_thickness: FloatProperty(
        name="cover thickness", default=0.002, min=.0, step=.02, unit="LENGTH", update=update) # TODO hinge_inset_guard
    rndm_cover_thickness_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    textblock_offset: FloatProperty(
        name="textblock offset", default=0.005, min=.0, step=.001, unit="LENGTH", update=update)
    rndm_textblock_offset_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    spine_curl: FloatProperty(
        name="spine curl", default=0.002, step=.002, min=.0, unit="LENGTH", update=update)
    rndm_spine_curl_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    hinge_inset: FloatProperty(
        name="hinge inset", default=0.001, min=.0, step=.0001, unit="LENGTH", update=update) #TODO hinge inset guard
    rndm_hinge_inset_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    hinge_width: FloatProperty(
        name="hinge width", default=0.004, min=.0, step=.05, unit="LENGTH", update=update)
    rndm_hinge_width_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    subsurf: BoolProperty(
        name="Add Subsurf-Modifier", default=False, update=update)


    material: PointerProperty(name="Material", type=bpy.types.Material)
