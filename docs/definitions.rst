Definitions of concepts used in PyWO
=========================================================

.. _desktop:

Desktop
------------------
Window Manager may create one or more "virtual" desktops, 
their size may be bigger than the size of the :ref:`screen`.

.. _viewport:

Viewport
------------------
If :ref:`desktop` size is bigger than :ref:`screen` size :ref:`viewport` is a part of
Desktop that is currently visible.

.. _workarea:

Workarea
------------------
Part of :ref:`viewport` that can be used by Windows. 
Windows with strut defined (panels, pagers, etc) may reserve space
on the edges of :ref:`viewport`.
Workarea size may be bigger than :ref:`screen` size.
  
.. _screen:

Screen
------------------
Physical monitor screen. If multiple monitors screens are used,
and Xinerama extension is available :ref:`screen` shows part of :ref:`workarea`.

.. _action:

Action
-----------------
Callable (function or :class:`pywo.actions.core.Action` instance) that changes window(s) or window manager state. Form simple ones like changing windows state (maximizing, shading), to complex ones like putting on the grid.

.. _service:

Service
-----------------
Background task providing additional features, or means of communication with PyWO. Built in services are `deamon` allowing PyWO to be run as daemon, `keyboard_service` responsible for handling keyboard shortcuts, and `dbus_service` allowing communication with running PyWO daemon using D-Bus.

