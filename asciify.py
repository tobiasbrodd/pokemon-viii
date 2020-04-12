from PIL import Image
from enum import Enum


class Scale(Enum):
    TEN = " .:-=+*#%@"
    STANDARD = " .'`^\",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    COLOR = "#%@"


def get_image(path):
    try:
        image = Image.open(path)
        return image
    except Exception as error:
        print(error)
        return None


def resize(image, new_width=100):
    (width, height) = image.size
    aspect_ratio = float(height) / float(width)
    new_height = int(aspect_ratio * new_width / 2)
    dim = (new_width, new_height)

    return image.resize(dim)


def to_greyscale(image):
    return image.convert("L")


def color(s, r, g, b):
    return f"\033[38;2;{r};{g};{b}m{s}\033[0m"


def to_ascii(image, scale=Scale.TEN):
    ASCII_CHARS = scale.value
    pixels = list(image.getdata())
    buckets = (255 // len(ASCII_CHARS)) + 1
    ascii_pixels = [ASCII_CHARS[p // buckets] for p in pixels]

    return "".join(ascii_pixels)


def to_ascii_color(image, image_grey, scale=Scale.COLOR):
    ASCII_CHARS = scale.value
    colored_pixels = list(image.getdata())
    grey_pixels = list(image_grey.getdata())
    pixel_colors = [(p[0], p[1], p[2]) for p in colored_pixels]

    buckets = (255 // len(ASCII_CHARS)) + 1
    ascii_pixels = []
    for (i, p) in enumerate(grey_pixels):
        rgb = pixel_colors[i]
        if rgb == (0, 0, 0):
            ascii_pixels.append(" ")
        else:
            ascii_pixels.append(ASCII_CHARS[p // buckets])

    return "".join(ascii_pixels), pixel_colors


def convert_grey(image, width=100, scale=Scale.TEN):
    image = resize(image, new_width=width)
    image = to_greyscale(image)

    ascii_pixels = to_ascii(image)
    n = len(ascii_pixels)
    ascii_image = [ascii_pixels[i : i + width] for i in range(0, n, width)]

    return ascii_image


def convert_color(image, width=100, scale=Scale.COLOR):
    image = resize(image, new_width=width)
    image_grey = to_greyscale(image)

    ascii_pixels, pixel_colors = to_ascii_color(image, image_grey)
    n = len(ascii_pixels)
    colored_ascii_pixels = []
    for (i, pixel) in enumerate(ascii_pixels):
        rgb = pixel_colors[i]
        colored_pixel = color(pixel, rgb[0], rgb[1], rgb[2])
        colored_ascii_pixels.append(colored_pixel)
    colored_ascii_image = [
        colored_ascii_pixels[i : i + width] for i in range(0, n, width)
    ]
    colored_ascii_image = ["".join(row) for row in colored_ascii_image]

    return colored_ascii_image


def convert(image, width=100, scale=Scale.TEN, color=False):
    if color:
        return convert_color(image, width=width, scale=scale)
    else:
        return convert_grey(image, width=width, scale=scale)
