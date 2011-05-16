#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '../')
sys.path.insert(0, './')

from tests.common_test import MockedXlibTests
from tests.common_test import DESKTOP_WIDTH, DESKTOP_HEIGHT

from pywo import core
from pywo.actions import manipulate


TOP_LEFT = core.Gravity.parse('NW')
TOP = core.Gravity.parse('N')
TOP_RIGHT = core.Gravity.parse('NE')
LEFT = core.Gravity.parse('W')
ALL = core.Gravity.parse('MIDDLE')
RIGHT = core.Gravity.parse('E')
BOTTOM_LEFT = core.Gravity.parse('SW')
BOTTOM = core.Gravity.parse('S')
BOTTOM_RIGHT = core.Gravity.parse('SE')


class In_GeometryTests(MockedXlibTests):

    def test_in_axis_geometry(self):
        geometry = self.win.geometry
        in_axis = manipulate.in_axis_geometry(geometry, 'x')
        self.assertEqual(in_axis, 
                         core.Geometry(geometry.x, 0,
                                       geometry.width, DESKTOP_HEIGHT))

        in_axis = manipulate.in_axis_geometry(geometry, 'y')
        self.assertEqual(in_axis, 
                         core.Geometry(0, geometry.y,
                                       DESKTOP_WIDTH, geometry.height))

    def test_in_direction_geometry(self):
        geometry = self.win.geometry
        workarea = self.WM.workarea_geometry
        in_direction = manipulate.in_direction_geometry(geometry, ALL)
        self.assertEqual(in_direction, self.WM.workarea_geometry)

        in_direction = manipulate.in_direction_geometry(geometry, TOP_LEFT)
        self.assertEqual(in_direction,
                         core.Geometry(0, 0, geometry.x, geometry.y))

        in_direction = manipulate.in_direction_geometry(geometry, TOP)
        self.assertEqual(in_direction,
                         core.Geometry(0, 0, workarea.width, geometry.y))

        in_direction = manipulate.in_direction_geometry(geometry, TOP_RIGHT)
        self.assertEqual(in_direction,
                         core.Geometry(geometry.x2, 0,
                                       workarea.width - geometry.x2, geometry.y))

        in_direction = manipulate.in_direction_geometry(geometry, LEFT)
        self.assertEqual(in_direction,
                         core.Geometry(0, 0, geometry.x, workarea.height))

        in_direction = manipulate.in_direction_geometry(geometry, RIGHT)
        self.assertEqual(in_direction,
                         core.Geometry(geometry.x2, 0,
                                       workarea.width - geometry.x2, workarea.height))

        in_direction = manipulate.in_direction_geometry(geometry, BOTTOM_LEFT)
        self.assertEqual(in_direction,
                         core.Geometry(0, geometry.y2,
                                       geometry.x, workarea.height - geometry.y2))

        in_direction = manipulate.in_direction_geometry(geometry, BOTTOM)
        self.assertEqual(in_direction,
                         core.Geometry(0, geometry.y2,
                                       workarea.width, workarea.height - geometry.y2))

        in_direction = manipulate.in_direction_geometry(geometry, BOTTOM_RIGHT)
        self.assertEqual(in_direction,
                         core.Geometry(geometry.x2, geometry.y2,
                                       workarea.width - geometry.x2,
                                       workarea.height - geometry.y2))


    def test_in_direction_geometry__inclusive(self):
        geometry = self.win.geometry
        workarea = self.WM.workarea_geometry
        in_direction = manipulate.in_direction_geometry(geometry, ALL, True)
        self.assertEqual(in_direction, self.WM.workarea_geometry)

        in_direction = manipulate.in_direction_geometry(geometry, TOP_LEFT, True)
        self.assertEqual(in_direction,
                         core.Geometry(0, 0, geometry.x2, geometry.y2))

        in_direction = manipulate.in_direction_geometry(geometry, TOP, True)
        self.assertEqual(in_direction,
                         core.Geometry(0, 0, workarea.width, geometry.y2))

        in_direction = manipulate.in_direction_geometry(geometry, TOP_RIGHT, True)
        self.assertEqual(in_direction,
                         core.Geometry(geometry.x, 0,
                                       workarea.width - geometry.x, geometry.y2))

        in_direction = manipulate.in_direction_geometry(geometry, LEFT, True)
        self.assertEqual(in_direction,
                         core.Geometry(0, 0, geometry.x2, workarea.height))

        in_direction = manipulate.in_direction_geometry(geometry, RIGHT, True)
        self.assertEqual(in_direction,
                         core.Geometry(geometry.x, 0,
                                       workarea.width - geometry.x, workarea.height))

        in_direction = manipulate.in_direction_geometry(geometry, BOTTOM_LEFT, True)
        self.assertEqual(in_direction,
                         core.Geometry(0, geometry.y,
                                       geometry.x2, workarea.height - geometry.y))

        in_direction = manipulate.in_direction_geometry(geometry, BOTTOM, True)
        self.assertEqual(in_direction,
                         core.Geometry(0, geometry.y,
                                       workarea.width, workarea.height - geometry.y))

        in_direction = manipulate.in_direction_geometry(geometry, BOTTOM_RIGHT, True)
        self.assertEqual(in_direction,
                         core.Geometry(geometry.x, geometry.y,
                                       workarea.width - geometry.x,
                                       workarea.height - geometry.y))


class ExpandWindowTests(MockedXlibTests):

    def setUp(self):
        MockedXlibTests.setUp(self)
        self.resize = manipulate.Expander()

    def test_empty_desktop(self):
        geometry = self.win.geometry
        resized = self.resize(self.win, TOP_LEFT)
        self.assertEqual(resized.x, 0)
        self.assertEqual(resized.y, 0)
        self.assertEqual(resized.x2, geometry.x2)
        self.assertEqual(resized.y2, geometry.y2)
        self.win.set_geometry(geometry)

        resized = self.resize(self.win, TOP)
        self.assertEqual(resized.x, geometry.x)
        self.assertEqual(resized.y, 0)
        self.assertEqual(resized.x2, geometry.x2)
        self.assertEqual(resized.y2, geometry.y2)
        self.win.set_geometry(geometry)

        resized = self.resize(self.win, TOP_RIGHT)
        self.assertEqual(resized.x, geometry.x)
        self.assertEqual(resized.y, 0)
        self.assertEqual(resized.x2, DESKTOP_WIDTH)
        self.assertEqual(resized.y2, geometry.y2)
        self.win.set_geometry(geometry)

        resized = self.resize(self.win, LEFT)
        self.assertEqual(resized.x, 0)
        self.assertEqual(resized.y, geometry.y)
        self.assertEqual(resized.x2, geometry.x2)
        self.assertEqual(resized.y2, geometry.y2)
        self.win.set_geometry(geometry)

        resized = self.resize(self.win, ALL)
        self.assertEqual(resized.x, 0)
        self.assertEqual(resized.y, 0)
        self.assertEqual(resized.x2, DESKTOP_WIDTH)
        self.assertEqual(resized.y2, DESKTOP_HEIGHT)
        self.win.set_geometry(geometry)

        resized = self.resize(self.win, RIGHT)
        self.assertEqual(resized.x, geometry.x)
        self.assertEqual(resized.y, geometry.y)
        self.assertEqual(resized.x2, DESKTOP_WIDTH)
        self.assertEqual(resized.y2, geometry.y2)
        self.win.set_geometry(geometry)

        resized = self.resize(self.win, BOTTOM_LEFT)
        self.assertEqual(resized.x, 0)
        self.assertEqual(resized.y, geometry.y)
        self.assertEqual(resized.x2, geometry.x2)
        self.assertEqual(resized.y2, DESKTOP_HEIGHT)
        self.win.set_geometry(geometry)

        resized = self.resize(self.win, BOTTOM_RIGHT)
        self.assertEqual(resized.x, geometry.x)
        self.assertEqual(resized.y, geometry.y)
        self.assertEqual(resized.x2, DESKTOP_WIDTH)
        self.assertEqual(resized.y2, DESKTOP_HEIGHT)

    def test_maximal_size(self):
        max_geometry = core.Geometry(0, 0, DESKTOP_WIDTH, DESKTOP_HEIGHT)
        self.win.set_geometry(max_geometry)
        resized = self.resize(self.win, ALL)
        self.assertEqual(resized.x, 0)
        self.assertEqual(resized.y, 0)
        self.assertEqual(resized.x2, DESKTOP_WIDTH)
        self.assertEqual(resized.y2, DESKTOP_HEIGHT)


class ShrinkWindowTests(MockedXlibTests):

    def setUp(self):
        MockedXlibTests.setUp(self)
        self.resize = manipulate.Shrinker()

    def test_empty_desktop(self):
        geometry = self.win.geometry
        resized = self.resize(self.win, TOP_LEFT)
        self.assertEqual(resized, geometry)
        resized = self.resize(self.win, TOP)
        self.assertEqual(resized, geometry)
        resized = self.resize(self.win, TOP_RIGHT)
        self.assertEqual(resized, geometry)
        resized = self.resize(self.win, LEFT)
        self.assertEqual(resized, geometry)
        resized = self.resize(self.win, ALL)
        self.assertEqual(resized, geometry)
        resized = self.resize(self.win, RIGHT)
        self.assertEqual(resized, geometry)
        resized = self.resize(self.win, BOTTOM_LEFT)
        self.assertEqual(resized, geometry)
        resized = self.resize(self.win, BOTTOM)
        self.assertEqual(resized, geometry)
        resized = self.resize(self.win, BOTTOM_RIGHT)
        self.assertEqual(resized, geometry)


if __name__ == '__main__':
    main_suite = unittest.TestSuite()
    for suite in [In_GeometryTests, 
                  ExpandWindowTests,
                  ShrinkWindowTests, ]:
        main_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    unittest.TextTestRunner(verbosity=2).run(main_suite)

