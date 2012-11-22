#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    sys.path.append(os.path.normpath(os.path.join(os.path.realpath(__file__), '../..')))
    sys.path.append(os.path.normpath(os.path.join(os.path.realpath(__file__), '../../../contrib')))
    sys.path.append(os.path.normpath(os.path.join(os.path.realpath(__file__), '../../../../config')))

    if len(sys.argv) > 1 and sys.argv[-1] in ('hiking', 'cycling', 'skating', 'mtbmap'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "routemap.sites." + sys.argv[-1] + ".settings" )
        execute_from_command_line(sys.argv[:-1])
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "routemap.sites.hiking.settings" )
        execute_from_command_line(sys.argv)
