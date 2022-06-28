#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!
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

def apply_per_pixel(image, func):
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
        temp2 = func(temp1)
        result['pixels'].append(temp2)
    return result

def inverted(image):
    return apply_per_pixel(image, lambda s: 255 - s)


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

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
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


def save_image(image, filename, mode='PNG'):
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
    
    bluegill1 = load_image('bluegill.png')
    bluegill2 = inverted(bluegill1)
    save_image(bluegill2, 'bluegill2.png', mode = 'PNG')
    
    kernelite = []
    for i in range(81):
        if i == 18:
            kernelite.append(1)
        else:
            kernelite.append(0)
    
    pigbird1 = load_image('pigbird.png')
    pigbird2 = correlate(pigbird1, kernelite)
    pigbird3 = round_and_clip_image(pigbird2)
    save_image(pigbird3, 'pigbird2.png', mode = 'PNG')
    
    cat1 = load_image('cat.png')
    cat2 = blurred(cat1, 5)
    save_image(cat2, 'cat2.png', mode = 'PNG')
    
    python1 = load_image('python.png')
    python2 = sharpened(python1, 11)
    save_image(python2, 'python2.png', mode = 'PNG')
    
    construct1 = load_image('construct.png')
    construct2 = edges(construct1)
    save_image(construct2, 'construct2.png', mode = 'PNG')
    pass
