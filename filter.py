from struct import unpack
from scipy import interpolate

from PIL import Image
import numpy
import scipy

import sys


class Filter:

    def __init__(self, acv_file_path, name):
        self.name = name
        with open(acv_file_path, 'rb') as acv_file:
            self.curves = self._read_curves(acv_file)
        self.polynomials = self._find_coefficients()

    def _read_curves(self, acv_file):
        _, nr_curves = unpack('!hh', acv_file.read(4))
        curves = []
        for i in range(0, nr_curves):
            curve = []
            num_curve_points, = unpack('!h', acv_file.read(2))
            for j in range(0, num_curve_points):
                y, x = unpack('!hh', acv_file.read(4))
                curve.append((x, y))
            curves.append(curve)

        return curves

    def _find_coefficients(self):
        polynomials = []
        for curve in self.curves:
            xdata = [x[0] for x in curve]
            ydata = [x[1] for x in curve]
            p = interpolate.lagrange(xdata, ydata)
            polynomials.append(p)
        return polynomials

    def get_r(self):
        return self.polynomials[1]

    def get_g(self):
        return self.polynomials[2]

    def get_b(self):
        return self.polynomials[3]

    def get_c(self):
        return self.polynomials[0]


class FilterManager:

    def __init__(self):
        self.filters = {}
        # add some stuff here

    def add_filter(self, filter_obj):
        # Overwrites if such a filter already exists
        # NOTE: Fix or not to fix?
        self.filters[filter_obj.name] = filter_obj

    def apply_filter(self, filter_name, image_array):

        if image_array.ndim < 3:
            raise Exception('Photos must be in color, meaning at least 3 channels')
        else:
            def interpolate(i_arr, f_arr, p, p_c):
                p_arr = p_c(f_arr)
                return p_arr

                # NOTE: Assumes that image_array is a numpy array

            image_filter = self.filters[filter_name]
            # NOTE: What happens if filter does not exist?
            width, height, channels = image_array.shape
            filter_array = numpy.zeros((width, height, 3), dtype=float)

            p_r = image_filter.get_r()
            p_g = image_filter.get_g()
            p_b = image_filter.get_b()
            p_c = image_filter.get_c()

            filter_array[:, :, 0] = p_r(image_array[:, :, 0])
            filter_array[:, :, 1] = p_g(image_array[:, :, 1])
            filter_array[:, :, 2] = p_b(image_array[:, :, 2])
            filter_array = filter_array.clip(0, 255)
            filter_array = p_c(filter_array)

            filter_array = numpy.ceil(filter_array).clip(0, 255)

            return filter_array.astype(numpy.uint8)


def create_filters(img):
    img = Image.open(img)
    image_array = numpy.array(img)

    im = Image.fromarray(image_array)
    im.save('static/img/filtered/1.png')

    image_array = numpy.array(img)
    img_filter = Filter("curves/country.acv", 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)

    filter_array = filter_manager.apply_filter('crgb', image_array)

    im = Image.fromarray(filter_array)
    im.save('static/img/filtered/2.png')

    image_array = numpy.array(img)
    img_filter = Filter("curves/crossprocess.acv", 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)

    filter_array = filter_manager.apply_filter('crgb', image_array)

    im = Image.fromarray(filter_array)
    im.save('static/img/filtered/3.png')

    image_array = numpy.array(img)
    img_filter = Filter("curves/desert.acv", 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)

    filter_array = filter_manager.apply_filter('crgb', image_array)

    im = Image.fromarray(filter_array)
    im.save('static/img/filtered/4.png')

    image_array = numpy.array(img)
    img_filter = Filter("curves/lumo.acv", 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)

    filter_array = filter_manager.apply_filter('crgb', image_array)

    im = Image.fromarray(filter_array)
    im.save('static/img/filtered/5.png')

    image_array = numpy.array(img)
    img_filter = Filter("curves/nashville.acv", 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)

    filter_array = filter_manager.apply_filter('crgb', image_array)

    im = Image.fromarray(filter_array)
    im.save('static/img/filtered/6.png')

    image_array = numpy.array(img)
    img_filter = Filter("curves/portraesque.acv", 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)

    filter_array = filter_manager.apply_filter('crgb', image_array)

    im = Image.fromarray(filter_array)
    im.save('static/img/filtered/7.png')

    image_array = numpy.array(img)
    img_filter = Filter("curves/proviaesque.acv", 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)

    filter_array = filter_manager.apply_filter('crgb', image_array)

    im = Image.fromarray(filter_array)
    im.save('static/img/filtered/8.png')

    image_array = numpy.array(img)
    img_filter = Filter("curves/velviaesque.acv", 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)

    filter_array = filter_manager.apply_filter('crgb', image_array)

    im = Image.fromarray(filter_array)
    im.save('static/img/filtered/9.png')


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Wrong number of arguments")
        print("""  Usage: \
              python filter.py imagefile] """)
    else:
        create_filters(sys.argv[-1])
