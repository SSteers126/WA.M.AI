def resize_dimensions_with_aspect(dimension1, dimension2, dimension1_new):
    scale_factor = dimension1_new / float(dimension1)  # Ensure output is a float for more accurate results
    dimension2_new = int(dimension2 * scale_factor)
    return dimension1_new, dimension2_new

width, height = 400, 300


print(resize_dimensions_with_aspect(width, height, 600))
print(resize_dimensions_with_aspect(height, width, 600))
