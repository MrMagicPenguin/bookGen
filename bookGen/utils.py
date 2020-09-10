import os

import bpy
import bpy_extras.view3d_utils
from mathutils import Vector


def get_bookgen_collection(create=True):
    for c in bpy.context.scene.collection.children:
        if c.name == "BookGen":
            return c
    if create:
        col = bpy.data.collections.new("BookGen")
        bpy.context.scene.collection.children.link(col)
    else:
        col = None
    return col


def get_shelf_collection(name):
    bookgen = get_bookgen_collection()
    for c in bookgen.children:
        if c.name == name:
            return c

    col = bpy.data.collections.new(name)
    bookgen.children.link(col)
    return col


def get_shelf_collection_by_index(index):
    bookgen = get_bookgen_collection()
    if index < 0 or index >= len(bookgen.children):
        return None
    return bookgen.children[index]


def visible_objects_and_duplis():
    """Loop over (object, matrix) pairs (mesh only)"""

    depsgraph = bpy.context.evaluated_depsgraph_get()
    for dup in depsgraph.object_instances:
        if dup.is_instance:  # Real dupli instance
            obj = dup.instance_object
            yield (obj, dup.matrix_world.copy())
        else:  # Usual object
            obj = dup.object
            yield (obj, obj.matrix_world.copy())


def obj_ray_cast(obj, matrix, ray_origin, ray_target):
    """Wrapper for ray casting that moves the ray into object space"""

    # get the ray relative to the object
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj

    # cast the ray
    success, location, normal, face = obj.ray_cast(ray_origin_obj, ray_direction_obj)

    if success:
        return location, normal, face
    else:
        return None, None, None


def project_to_screen(context, world_space_point):
    """ Returns the 2d location of a world space point inside the 3D viewport """
    region = context.region
    rv3d = context.space_data.region_3d
    return bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, world_space_point, (0, 0))


bookGen_directory = os.path.dirname(os.path.realpath(__file__))


def get_shelf_parameters(shelf_id=0):
    properties = get_bookgen_collection().BookGenProperties

    parameters = {
        "scale": properties.scale,
        "seed": properties.seed + shelf_id,
        "alignment": properties.alignment,
        "lean_amount": properties.lean_amount,
        "lean_direction": properties.lean_direction,
        "lean_angle": properties.lean_angle,
        "rndm_lean_angle_factor": properties.rndm_lean_angle_factor,
        "book_height": properties.book_height,
        "rndm_book_height_factor": properties.rndm_book_height_factor,
        "book_width": properties.book_width,
        "rndm_book_width_factor": properties.rndm_book_width_factor,
        "book_depth": properties.book_depth,
        "rndm_book_depth_factor": properties.rndm_book_depth_factor,
        "cover_thickness": properties.cover_thickness,
        "rndm_cover_thickness_factor": properties.rndm_cover_thickness_factor,
        "textblock_offset": properties.textblock_offset,
        "rndm_textblock_offset_factor": properties.rndm_textblock_offset_factor,
        "spine_curl": properties.spine_curl,
        "rndm_spine_curl_factor": properties.rndm_spine_curl_factor,
        "hinge_inset": properties.hinge_inset,
        "rndm_hinge_inset_factor": properties.rndm_hinge_inset_factor,
        "hinge_width": properties.hinge_width,
        "rndm_hinge_width_factor": properties.rndm_hinge_width_factor,
        "subsurf": properties.subsurf,
        "cover_material": properties.cover_material,
        "page_material": properties.page_material
    }
    return parameters


def ray_cast(x, y):
    region = bpy.context.region
    region_data = bpy.context.space_data.region_3d

    view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, region_data, (x, y))
    ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, region_data, (x, y))

    ray_target = ray_origin + view_vector

    best_length_squared = -1.0
    closest_loc = None
    closest_normal = None
    closest_obj = None
    closest_face = None

    for obj, matrix in visible_objects_and_duplis():
        if obj.type == 'MESH':
            hit, normal, face = obj_ray_cast(obj, matrix, ray_origin, ray_target)
            if hit is not None:
                _, rot, _ = matrix.decompose()
                hit_world = matrix @ hit
                normal_world = rot.to_matrix() @ normal
                length_squared = (hit_world - ray_origin).length_squared
                if closest_loc is None or length_squared < best_length_squared:
                    best_length_squared = length_squared
                    closest_loc = hit_world
                    closest_normal = normal_world
                    closest_face = face
                    closest_obj = obj

    return closest_loc, closest_normal, closest_face, closest_obj


def get_click_face(x, y):
    _, _, closest_face, closest_obj = ray_cast(x, y)
    return closest_obj, closest_face


def get_click_position_on_object(x, y):
    closest_loc, closest_normal, _, _ = ray_cast(x, y)

    return closest_loc, closest_normal


def vector_scale(veca, vecb):
    return Vector(x * y for x, y in zip(veca, vecb))


def get_free_shelf_id():
    shelves = get_bookgen_collection().children

    names = list(map(lambda x: x.name, shelves))
    name_found = False
    shelf_id = 0
    while not name_found:
        if "shelf_" + str(shelf_id) not in names:
            return shelf_id
        shelf_id += 1
