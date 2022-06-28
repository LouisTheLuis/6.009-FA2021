#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# CODE FROM LAB 1 (replace with your code)
def get_pixel(image, x, y):
    """
    Returns the color value of a certain pixel. If the value of the x or y coordinate
    is out of bounds for the image, it returns the value of the closest in-bound pixel.
    """
    pixel = 0
    if x >= 0 and y >= 0 and x < image['width'] and y < image['height']:
        index = y * (image['width']) + x
        pixel = image['pixels'][index]
    else:
        #CORNERS
        if x < 0 and y < 0:
            pixel = image['pixels'][0]
        elif x < 0 and y >= image['height']:
            index = image['width'] * (image['height'] - 1)
            pixel = image['pixels'][index]
        elif x >= image['width'] and y < 0:
            index = image['width'] - 1 
            pixel = image['pixels'][index]
        elif x >= image['width'] and y >= image['height']:
            pixel = image['pixels'][-1]
        #SIDES
        elif x >= image['width'] and (y >= 0 and y < image['height']):
            index = (y + 1) * image['width'] - 1
            pixel = image['pixels'][index]
        elif x < 0 and (y >= 0 and y < image['height']):
            index = y * image['width']
            pixel = image['pixels'][index]
        elif (x >= 0 and x < image['width']) and y < 0:
            index = x
            pixel = image['pixels'][index]
        elif (x >= 0 and x < image['width']) and y >= image['height']:
            index = (image['width'] * (image['height'] - 1)) + x
            pixel = image['pixels'][index]
    return pixel

def set_pixel(image, x, y, kernel):
    """
    Sets the colors of a certain pixel given a certain kernel.
    """
    pixel = 0 
    set_range = []
    kernel_width = int(math.sqrt(len(kernel)))
    s = -math.floor(kernel_width/2)
    for i in range(kernel_width):
        set_range.append(s + i)
    for j in range(len(kernel)):
        x1 = x + set_range[j % kernel_width]
        y1 = y + set_range[int((j - (j % (kernel_width))) / kernel_width)]
        value = kernel[j] * get_pixel(image, x1, y1)
        pixel += value
    return pixel

def get_coordinates(image, indx):
    """
    Returns the coordinates of a certain index in the list of pixels of an image.
    """
    a = indx % image['width']
    b = int((indx - (indx % (image['width']))) / image['width'])
    return [a, b]

def apply_per_pixel(image):
    """
    Inverts the color of a certain pixel.
    """
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    for p in range(len(image['pixels'])):
        temp1 = image['pixels'][p]
        temp2 = 255 - temp1
        result['pixels'].append(temp2)
    return result

def inverted(image):
    return apply_per_pixel(image)


# HELPER FUNCTIONS

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    """
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
        }
    for i in range(len(image['pixels'])):
        coordinates = get_coordinates(image, i)
        temp = set_pixel(image, coordinates[0], coordinates[1], kernel)
        new_image['pixels'].append(temp)
    return new_image


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
        }
    for i in range(len(image['pixels'])):
        if image['pixels'][i] < 0:
            new_image['pixels'].append(0)
        elif image['pixels'][i] > 255:
            new_image['pixels'].append(255)
        else:
            temp = round(image['pixels'][i])
            new_image['pixels'].append(temp)
    return new_image


# FILTERS
def box_blur_kernel(size):
    """
    Generates a box blur kernel of a certain size.
    """
    kernel = []
    square = size ** 2
    for i in range(size):
        for j in range(size):
            kernel.append(1 / square)
    return kernel

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    box_kernel = box_blur_kernel(n)

    # then compute the correlation of the input image with that kernel
    result = correlate(image, box_kernel)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    new_result = round_and_clip_image(result)
    return new_result

def sharpened(image, n):
    """
    Returns a new image representing the result of a sharpen filter (or an unsharp mask)
    to a given input image, using a box blur of size n.
    
    This process should not mutate the input image; rather, it should create a separate 
    structure to represent the output.
    """
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
        }
    blur = blurred(image, n)
    
    for i in range(len(image['pixels'])):
        value = (2 * image['pixels'][i]) - blur['pixels'][i]
        new_image['pixels'].append(value)

    new_image2 = round_and_clip_image(new_image)
    return new_image2

def edges(image):
    """
    Returns a new image representing the result of a Sobel operator, using two kernels K_x
    and K_y, to a given input image.
    
    This process should not mutate the input image; rather, it should create a separate 
    structure to represent the output.  
    """
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
        }
    K_x = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
    K_y = [-1, -2, -1, 0, 0, 0, 1, 2, 1]
    image1 = correlate(image, K_x)
    image2 = correlate(image, K_y)
    
    for i in range(len(image['pixels'])):
        value = round(math.sqrt((image1['pixels'][i]**2) + (image2['pixels'][i]**2)))
        new_image['pixels'].append(value)
    
    new_image1 = round_and_clip_image(new_image)
    return new_image1
            

# LAB 2 HELPERS

def split_color(color_image):
    """
    Given a color image, it returns a list of dictionary with 5 elements:
    'height', 'width', 'red_pixels', 'green_pixels', 'blue_pixels'
    In other words, it splits the list of color tuples into three lists of pixels of each
    color.
    """
    new_dict = {
        'height': color_image['height'],
        'width': color_image['width'],
        'red_pixels': [],
        'green_pixels': [],
        'blue_pixels': []
        }
    for i in range(0, 3, 1):
        for j in range(len(color_image['pixels'])):
            if i == 0:
                new_dict['red_pixels'].append(color_image['pixels'][j][i])
            elif i == 1:
                new_dict['green_pixels'].append(color_image['pixels'][j][i])
            else:
                new_dict['blue_pixels'].append(color_image['pixels'][j][i])
    return new_dict

def unite_color(height, width, red_list, green_list, blue_list):
    """
    This function takes 3 lists of color pixels of an image, height and width of an image
    and it returns a color image (with a list of tuples for the colors).
    """
    new_image = {
        'height': height,
        'width': width,
        'pixels': []
        }
    for i in range(len(red_list)):
        temp_tuple = (red_list[i], green_list[i], blue_list[i])
        new_image['pixels'].append(temp_tuple)
    return new_image

def create_image(height, width, pixels):
    """ 
    This function creates a dictionary of an image given height, width, and a list
    of pixels.
    """
    new_image = {
        'height': height,
        'width': width,
        'pixels': pixels.copy()
        }
    return new_image

# LAB 2 FILTERS

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_filter(image):
        color_dict = split_color(image)
        
        # STATS BEING COLLECTED AFTER SPLITTING THE IMAGE
        height_cf = color_dict['height']
        width_cf = color_dict['width']
        
        rlist0 = create_image(height_cf, width_cf, color_dict['red_pixels'])
        glist0 = create_image(height_cf, width_cf, color_dict['green_pixels'])
        blist0 = create_image(height_cf, width_cf, color_dict['blue_pixels'])
        ####################################################
        rlist = filt(rlist0)['pixels']
        glist = filt(glist0)['pixels']
        blist = filt(blist0)['pixels']    
        new_image = unite_color(height_cf, width_cf, rlist, glist, blist)
        return new_image
    return color_filter


def make_blur_filter(n):
    """ 
    Given a number n, it returns a blur filter using a box blur of size n x n.
    """
    def blur_filter(image):
        new_image = blurred(image, n)
        return new_image
    return blur_filter


def make_sharpen_filter(n):
    """ 
    Given a number n, it returns a sharpen filter using a box blur of size n x n.
    """
    def sharpen_filter(image):
        new_image = sharpened(image, n)
        return new_image
    return sharpen_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    i = len(filters) - 1
    def filter_combination(image):
        new_image = {}
        i = 0
        while i < len(filters):
            if i == 0:
                new_image = filters[i](image)
                i += 1
            else:
                new_image = filters[i](new_image)
                i += 1
        return new_image
    return filter_combination

# HELPER FUNCTIONS FOR SEAM CARVING

def get_min(image, x, y):
    """
    For a certain coordinate in the second to last row of an image, it returns the
    minimum value of the upper adjacent pixels.
    """
    if y == 0:
        return 0
    else:
        left_most = get_pixel(image, x - 1, y - 1)
        middle_most = get_pixel(image, x, y - 1)
        right_most = get_pixel(image, x + 1, y - 1)
        temp_list = [left_most, middle_most, right_most]
        value = min(temp_list)
        return value

def indexed(image, x, y):
    """  
    Given the coordinates of a pixel, it returns its index in the pixels list of an image.
    """
    w = image['width']
    index = (y * w) + x
    return index

def get_row_min_coord(image, coord_list):
    """ 
    Given a list of coordinates, it returns the coordinate of the pixel with the
    minimum value in the list. If all the coordinates of the list return the same value,
    the function will return the first coordinate of the list.
    """
    min_group = coord_list[0]
    listvals = []
    pairs = {}
    for i in range(len(coord_list)):
        listvals.append(get_pixel(image, coord_list[i][0], coord_list[i][1]))
        pairs[get_pixel(image, coord_list[i][0], coord_list[i][1])] = i
    min_value = min(listvals)
    index = pairs[min_value]
    return coord_list[index]

def get_min_coord(image, temp_coord):
    """ 
    Given the coordinate of a pixel, it returns the coordinates of the upper adjacent
    pixel with the minimum value.
    """
    x = temp_coord[0]
    y = temp_coord[1]
    left = indexed(image, x - 1, y - 1)
    middle = indexed(image, x, y - 1)
    right = indexed(image, x + 1, y - 1)
    
    if x == 0:
        if image['pixels'][middle] <= image['pixels'][right]:
            return get_coordinates(image, middle)
        else:
            return get_coordinates(image, right)
    elif x == image['width'] - 1:
        if image['pixels'][left] <= image['pixels'][middle]:
            return get_coordinates(image, left)
        else:
            return get_coordinates(image, middle)
    else:
        if image['pixels'][left] <= image['pixels'][middle]:
            if image['pixels'][left] <= image['pixels'][right]:
                return get_coordinates(image, left)
            else:
                return get_coordinates(image, right)
        else:
            if image['pixels'][middle] <= image['pixels'][right]:
                return get_coordinates(image, middle)
            else:
                return get_coordinates(image, right)
    
# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    new_image = {}
    for i in range(ncols):
        if i == 0:
            greyscale_copy = greyscale_image_from_color_image(image)
            energy_map = compute_energy(greyscale_copy)
            cumulative_energy = cumulative_energy_map(energy_map)
            list_to_erase = minimum_energy_seam(cumulative_energy)
            new_image = image_without_seam(image, list_to_erase)
        else:
            greyscale_copy = greyscale_image_from_color_image(new_image)
            energy_map = compute_energy(greyscale_copy)
            cumulative_energy = cumulative_energy_map(energy_map)
            list_to_erase = minimum_energy_seam(cumulative_energy)
            new_image = image_without_seam(new_image, list_to_erase)         
    return new_image


# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
        }
    for i in range(len(image['pixels'])):
        r = image['pixels'][i][0]
        g = image['pixels'][i][1]
        b = image['pixels'][i][2]
        value = round((.299*r) + (.587*g) + (.114*b))
        new_image['pixels'].append(value)
    return new_image


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    new_image = edges(grey)
    return new_image


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    new_dict = {
        'height': energy['height'],
        'width': energy['width'],
        'pixels': []
        }
    for i in range(energy['width']):
        new_dict['pixels'].append(energy['pixels'][i])
    for j in range(energy['width'], len(energy['pixels']), 1):
        temp_coord = get_coordinates(energy, j)
        temp_coord_value = get_pixel(energy, temp_coord[0], temp_coord[1])
        temp_min = get_min(new_dict, temp_coord[0], temp_coord[1])
        new_dict['pixels'].append(temp_coord_value + temp_min)
    return new_dict


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    list_min_e_seam = []
    counter = 0
    
    # Values that are useful
    h = cem['height']
    w = cem['width']
    ########################
    
    for i in range(h - 1, -1, -1):
        if i == h - 1:
            bottom_list = []
            for j in range((h - 1) * w, h * w, 1):
                bottom_list.append(get_coordinates(cem, j))
            minimum_coord = get_row_min_coord(cem, bottom_list)
            minimum_index = indexed(cem, minimum_coord[0], minimum_coord[1])
            list_min_e_seam.append(minimum_index)
        else:
            temp_coord = get_coordinates(cem, list_min_e_seam[counter])
            minimum_coord = get_min_coord(cem, temp_coord) 
            minimum_index = indexed(cem, minimum_coord[0], minimum_coord[1])
            list_min_e_seam.append(minimum_index)
            counter += 1
            
    list_min_e_seam.reverse()
    return list_min_e_seam


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    new_image = {
        'height': image['height'],
        'width': image['width'] - 1,
        'pixels': []
        }
    for i in range(len(image['pixels'])):
        if i in seam:
            pass
        else:
            new_image['pixels'].append(image['pixels'][i])
    return new_image

def paste(image1, image2):
    """
    Given two images and a position (a tuple), it pastes the first image (smaller) to the second image (larger).
    The position given will correspond to the upper right corner of the smaller image.
    """
    pos = [None, None]
    width_threshold = image2['width'] - image1['width']
    height_threshold = image2['height'] - image1['height']
    pos[0] = int(input('Give a width position smaller or equal to ' + str(width_threshold) + ': '))
    pos[1] = int(input('Give a height position smaller or equal to ' + str(height_threshold) + ': '))
    new_image = {
        'height': image2['height'],
        'width': image2['width'],
        'pixels': image2['pixels'].copy()
        }
    if pos[0] > image2['width'] - image1['width']:
        assert 'PositionError'
    elif pos[1] > image2['height'] - image1['width']:
        assert 'PositionError'
    else:
        w = image1['width']
        h = image1['height']
        top_pixel = get_coordinates(image1, 0)
        position = get_pixel(image2, pos[0], pos[1])
        for j in range(w + 1):
            for k in range(h + 1):
                val = get_pixel(image1, j, k)
                ind_large = indexed(image2, pos[0] + j, pos[1] + k)
                new_image['pixels'][ind_large] = val
    return new_image

# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    """cat1 = load_color_image('cat.png')
    filter1 = color_filter_from_greyscale_filter(apply_per_pixel)
    cat2 = filter1(cat1)
    save_color_image(cat2, 'cat1.png', mode = 'PNG')"""
    
    """python1 = load_color_image('python.png')
    filter2 = color_filter_from_greyscale_filter(make_blur_filter(9))
    python2 = filter2(python1)
    save_color_image(python2, 'python1.png', mode = 'PNG')"""
    
    mushroom = load_color_image('smallmushroom.png')
    
    sparrowchick1 = load_color_image('sparrowchick.png')
    filter3 = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    sparrowchick2 = filter3(sparrowchick1)
    save_color_image(sparrowchick2, 'sparrowchick1.png', mode = 'PNG')
    
    frog1 = load_color_image('frog.png')
    filter4 = color_filter_from_greyscale_filter(edges)
    filter5 = color_filter_from_greyscale_filter(make_blur_filter(5))
    filt = filter_cascade([filter4, filter4, filter5, filter4])
    frog2 = filt(frog1)
    save_color_image(frog2, 'frog1.png', mode = 'PNG')

    wow = paste(mushroom, sparrowchick1)
    save_color_image(wow, 'wow.png', mode = 'PNG')
    
    """twocats1 = load_color_image('twocats.png')
    twocats2 = seam_carving(twocats1, 100)
    save_color_image(twocats2, 'twocats1.png', mode = 'PNG')"""
    
    """pattern1 = load_color_image('pattern.png')
    pattern2 = seam_carving(pattern1, 2)
    save_color_image(pattern2, 'pattern2.png', mode = 'PNG')"""
    pass
