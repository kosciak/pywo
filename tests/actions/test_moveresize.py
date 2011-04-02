#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '../')
sys.path.insert(0, './')

from tests.test_common import TestMockedCore
from tests.test_common import DESKTOP_WIDTH, DESKTOP_HEIGHT
from tests.test_common import WIN_WIDTH, WIN_HEIGHT

from pywo import actions, core


TOP_LEFT = core.Gravity.parse('NW')
TOP = core.Gravity.parse('N')
TOP_RIGHT = core.Gravity.parse('NE')
LEFT = core.Gravity.parse('W')
MIDDLE = core.Gravity.parse('MIDDLE')
RIGHT = core.Gravity.parse('E')
BOTTOM_LEFT = core.Gravity.parse('SW')
BOTTOM = core.Gravity.parse('S')
BOTTOM_RIGHT = core.Gravity.parse('SE')


class TestPositionChangingAction(TestMockedCore):

    def get_geometry(self, x, y):
        return core.Geometry(x, y, WIN_WIDTH, WIN_HEIGHT)


class TestActionPut(TestPositionChangingAction):

    def test_position(self):
        action = actions.manager.get('put')
        action(self.win, position=TOP_LEFT)
        geometry = self.get_geometry(0, 0)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=TOP)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH/2, 0)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=TOP_RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH-WIN_WIDTH, 0)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=LEFT)
        geometry = self.get_geometry(0, DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH/2, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH-WIN_WIDTH, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=BOTTOM_LEFT)
        geometry = self.get_geometry(0, DESKTOP_HEIGHT-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=BOTTOM)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH/2, 
                                     DESKTOP_HEIGHT-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=BOTTOM_RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH-WIN_WIDTH, 
                                     DESKTOP_HEIGHT-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)

    def test_position_gravity(self):
        action = actions.manager.get('put')
        action(self.win, position=MIDDLE, gravity=TOP_LEFT)
        geometry = self.get_geometry(DESKTOP_WIDTH/2, 
                                     DESKTOP_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE, gravity=TOP)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH/2, 
                                     DESKTOP_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE, gravity=TOP_RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH, 
                                     DESKTOP_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE, gravity=LEFT)
        geometry = self.get_geometry(DESKTOP_WIDTH/2, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE, gravity=MIDDLE)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH/2, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE, gravity=RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE, gravity=BOTTOM_LEFT)
        geometry = self.get_geometry(DESKTOP_WIDTH/2, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE, gravity=BOTTOM)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH/2, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE, gravity=BOTTOM_RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)

    def test_same_position_twice(self):
        action = actions.manager.get('put')
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH/2, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        action(self.win, position=MIDDLE)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, position=MIDDLE)
        self.assertEqual(self.win.geometry, geometry)


class TestActionFloat(TestPositionChangingAction):

    def test_empty_desktop(self):
        action = actions.manager.get('float')
        action(self.win, direction=MIDDLE)
        geometry = self.get_geometry(DESKTOP_WIDTH/2-WIN_WIDTH/2, 
                                     DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, direction=LEFT)
        geometry = self.get_geometry(0, DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, direction=TOP)
        geometry = self.get_geometry(0, 0)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, direction=RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH-WIN_WIDTH, 0)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, direction=BOTTOM_LEFT)
        geometry = self.get_geometry(0, DESKTOP_HEIGHT-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, direction=TOP_RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH-WIN_WIDTH, 0)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, direction=BOTTOM)
        geometry = self.get_geometry(DESKTOP_WIDTH-WIN_WIDTH, 
                                     DESKTOP_HEIGHT-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, direction=TOP_LEFT)
        geometry = self.get_geometry(0, 0)
        self.assertEqual(self.win.geometry, geometry)
        action(self.win, direction=BOTTOM_RIGHT)
        geometry = self.get_geometry(DESKTOP_WIDTH-WIN_WIDTH, 
                                     DESKTOP_HEIGHT-WIN_HEIGHT)
        self.assertEqual(self.win.geometry, geometry)

    def test_same_direction_twice(self):
        action = actions.manager.get('float')
        action(self.win, direction=MIDDLE)
        action(self.win, direction=LEFT)
        geometry = self.get_geometry(0, DESKTOP_HEIGHT/2-WIN_HEIGHT/2)
        action(self.win, direction=LEFT)
        geometry = self.get_geometry(0, DESKTOP_HEIGHT/2-WIN_HEIGHT/2)


if __name__ == '__main__':
    main_suite = unittest.TestSuite()
    for suite in [TestActionPut, 
                  TestActionFloat, ]:
        main_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    unittest.TextTestRunner(verbosity=2).run(main_suite)
