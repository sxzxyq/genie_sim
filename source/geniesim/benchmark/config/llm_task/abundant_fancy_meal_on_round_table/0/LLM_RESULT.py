from helper import *

"""
scene_name: abundant_fancy_meal_on_round_table
description: An abundant fancy meal with drinks arranged on a round dining table.
"""


@register()
def place_items_on_round_table(table_shape: Shape, items: Shape) -> Shape:
    """
    Places a group of items (meal and drinks) onto the top surface of a round table.
    Ensures items are within the table's bounds and do not collide.
    """
    # Get table info in world frame
    table_info = get_object_info(table_shape)
    
    # Assume the table has a subpart named 'top' or 'surface'; if not, use overall top
    try:
        top_info = get_subpart_info(object_id="table_001", subpart_id="top")
        table_top_z_offset = top_info["xyz_max"][2]  # height from table center to top surface
    except KeyError:
        # Fallback: use overall table bounding box
        table_top_z_offset = table_info["size"][2] / 2.0

    # Table top center in world coordinates (z at surface level)
    table_top_center_world = np.array([
        table_info["center"][0],
        table_info["center"][1],
        table_info["center"][2] + table_top_z_offset
    ])
    
    # Place items at the center of the table top
    items_placed = transform_shape(
        items,
        translation_matrix([
            table_top_center_world[0],
            table_top_center_world[1],
            table_top_center_world[2]
        ])
    )
    
    return concat_shapes(table_shape, items_placed)


@register()
def create_fancy_meal_group() -> Shape:
    """
    Creates a group of fancy meal items: salads and oatmeal in ceramic bowls.
    """
    # Green salad
    green_salad = library_call(
        "usd",
        oid="benchmark_food_020",
        keywords=["green_salad", "fancy_meal", "salad", "white_plate", "left"]
    )
    
    # Mixed salad
    mixed_salad = library_call(
        "usd",
        oid="benchmark_food_022",
        keywords=["mixed_salad", "fancy_meal", "salad", "blue_bowl", "right"]
    )
    
    # Oatmeal in ceramic bowl
    oatmeal = library_call(
        "usd",
        oid="benchmark_food_018",
        keywords=["oatmeal", "fancy_breakfast", "ceramic_bowl", "gold_pattern", "front"]
    )
    
    # Arrange them in a triangular layout
    green_salad = transform_shape(green_salad, translation_matrix([-0.2, -0.15, 0.0]))
    mixed_salad = transform_shape(mixed_salad, translation_matrix([0.2, -0.15, 0.0]))
    oatmeal = transform_shape(oatmeal, translation_matrix([0.0, 0.2, 0.0]))
    
    return concat_shapes(green_salad, mixed_salad, oatmeal)


@register()
def create_drinks_group() -> Shape:
    """
    Creates a group of drinks: bottled beverages and glass tumblers.
    """
    # Select representative bottles
    red_bottle = library_call(
        "usd",
        oid="benchmark_beverage_bottle_004",
        keywords=["red_soda_bottle", "drink", "beverage", "left_front"]
    )
    
    white_bottle = library_call(
        "usd",
        oid="genie_beverage_bottle_015",
        keywords=["white_water_bottle", "drink", "beverage", "right_front"]
    )
    
    # Glass tumblers (liquid-filled)
    tumblers = library_call(
        "usd",
        oid="benchmark_desk_decoration_015",
        keywords=["glass_tumblers", "drink", "glassware", "back"]
    )
    
    # Position drinks around the meal
    red_bottle = transform_shape(red_bottle, translation_matrix([-0.25, 0.25, 0.0]))
    white_bottle = transform_shape(white_bottle, translation_matrix([0.25, 0.25, 0.0]))
    tumblers = transform_shape(tumblers, translation_matrix([0.0, -0.3, 0.0]))
    
    return concat_shapes(red_bottle, white_bottle, tumblers)


@register()
def abundant_fancy_meal_on_round_table() -> Shape:
    """
    Main scene: round table with abundant fancy meal and drinks.
    """
    # Load round table (light wood top, black base)
    table = library_call(
        "usd",
        oid="table_001",
        keywords=["round_dining_table", "table", "light_wood", "black_base", "fancy_dining"]
    )
    
    # Create and combine all items
    all_items = concat_shapes(
        library_call("create_fancy_meal_group"),
        library_call("create_drinks_group")
    )
    
    # Place on table
    return place_items_on_round_table(table, all_items)


@register()
def root_scene() -> Shape:
    return abundant_fancy_meal_on_round_table()