#!/usr/bin/env python3

import os
import lab
import types
import pickle
import hashlib
import collections

import pytest

from test import object_hash, compare_greyscale_images, compare_color_images, load_greyscale_image

TEST_DIRECTORY = os.path.dirname(__file__)


def test_greyscale():
    for fname in ('centered_pixel', 'pattern', 'smallfrog', 'bluegill', 'twocats', 'tree'):
        inpfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
        im = lab.load_color_image(inpfile)
        oim = object_hash(im)

        grey = lab.greyscale_image_from_color_image(im)
        expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_grey.png')
        assert object_hash(im) == oim, 'Be careful not to modify the original image!'
        compare_greyscale_images(grey, load_greyscale_image(expfile))


def test_energy():
    for fname in ('centered_pixel', 'pattern', 'smallfrog', 'bluegill', 'twocats', 'tree'):
        inpfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
        im = load_greyscale_image(inpfile)
        oim = object_hash(im)
        result = lab.compute_energy(im)
        assert object_hash(im) == oim, 'Be careful not to modify the original image!'

        expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_energy.pickle')
        with open(expfile, 'rb') as f:
            energy = pickle.load(f)

        compare_greyscale_images(result, energy)


def test_cumulative_energy():
    for fname in ('centered_pixel', 'pattern', 'smallfrog', 'bluegill', 'twocats', 'tree'):
        infile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_energy.pickle')
        with open(infile, 'rb') as f:
            energy = pickle.load(f)
        result = lab.cumulative_energy_map(energy)

        expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_cumulative_energy.pickle')
        with open(expfile, 'rb') as f:
            cem = pickle.load(f)

        compare_greyscale_images(result, cem)


def test_min_seam_indices():
    for fname in ('centered_pixel', 'pattern', 'smallfrog', 'bluegill', 'twocats', 'tree'):
        infile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_cumulative_energy.pickle')
        with open(infile, 'rb') as f:
            cem = pickle.load(f)
        result = lab.minimum_energy_seam(cem)

        expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_minimum_energy_seam.pickle')
        with open(expfile, 'rb') as f:
            seam = pickle.load(f)

        assert len(result) == len(seam)
        assert set(result) == set(seam)


def test_seam_removal():
    for fname in ('pattern', 'bluegill', 'twocats', 'tree'):
        infile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_minimum_energy_seam.pickle')
        with open(infile, 'rb') as f:
            seam = pickle.load(f)

        imfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
        result = lab.image_without_seam(lab.load_color_image(imfile), seam)

        expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_1seam.png')
        compare_color_images(result, lab.load_color_image(expfile))



if __name__ == '__main__':
    import sys
    import json

    class TestData:
        def __init__(self):
            self.results = {'passed': []}

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtestloop(self, session):
            yield

        def pytest_runtest_logreport(self, report):
            if report.when != 'call':
                return
            self.results.setdefault(report.outcome, []).append(report.head_line)

        def pytest_collection_finish(self, session):
            self.results['total'] = [i.name for i in session.items]

        def pytest_unconfigure(self, config):
            print(json.dumps(self.results))

    if os.environ.get('CATSOOP'):
        args = ['--color=yes', '-v', __file__]
        if len(sys.argv) > 1:
            args = ['-k', sys.argv[1], *args]
        kwargs = {'plugins': [TestData()]}
    else:
        args = ['-v', __file__] if len(sys.argv) == 1 else ['-v', *('%s::%s' % (__file__, i) for i in sys.argv[1:])]
        kwargs = {}
    res = pytest.main(args, **kwargs)
