from getopt import getopt, GetoptError
from PIL import Image
import sys


ASCII_CHARS = [".", ",", ":", ";", "+", "*", "?", "%", "$", "#", "@"]
# ASCII_CHARS = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~i!lI;:,"^`. '


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

    return "\n".join(ascii_image)


def main(argv):
    global ASCII_CHARS

    short_options = "h"
    long_options = ["help", "path=", "width=", "invert"]
    help_message = """usage: download.py [options]
    options:
        -h, --help          Prints help message.
        --path p            Path to image.
        --width w           Sets ASCII image width to 'w'.
        --invert            Inverts ASCII greyscale."""

    try:
        opts, args = getopt(argv, shortopts=short_options, longopts=long_options)
    except GetoptError:
        print(help_message)
        return

    path = None
    width = 100
    invert = False

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(help_message)
            return
        elif opt == "--path":
            path = arg
        elif opt == "--width":
            width = int(arg)
        elif opt == "--invert":
            invert = True

    image = get_image(path)

    if image is None:
        print(help_message)
        return

    if invert:
        ASCII_CHARS = ASCII_CHARS[::-1]

    ascii_image = convert(image, width=width)

    print(ascii_image)


if __name__ == "__main__":
    main(sys.argv[1:])
