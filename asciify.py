from PIL import Image


ASCII_CHARS = [" ", ".", ",", ":", ";", "+", "*", "?", "%", "$", "#", "@"]


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


def to_ascii(image):
    pixels = list(image.getdata())
    buckets = (255 // len(ASCII_CHARS)) + 1
    ascii_pixels = [ASCII_CHARS[p // buckets] for p in pixels]

    return "".join(ascii_pixels)


def convert(image, width=100):
    image = resize(image, new_width=width)
    image = to_greyscale(image)

    ascii_pixels = to_ascii(image)
    n = len(ascii_pixels)
    ascii_image = [ascii_pixels[i : i + width] for i in range(0, n, width)]

    return ascii_image
