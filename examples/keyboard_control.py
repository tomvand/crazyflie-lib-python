# Example usage of curses for control

import curses
import curses.panel
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander


URI = 'radio://0/80/250K'


def main(stdscr):
    curses.curs_set(False)
    stdscr.nodelay(True)

    stdscr.clear()
    stdscr.addstr(0, 0, 'Keyboard control demo\n', curses.A_REVERSE)
    stdscr.refresh()

    cflib.crtp.init_drivers(enable_debug_driver=False)
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        stdscr.clear()
        stdscr.addstr(0, 0, 'Keyboard control demo\n', curses.A_REVERSE)
        stdscr.addstr("Press 's' to start and 'q' to quit...\n")
        stdscr.refresh()

        c = -1
        while c == -1:
            c = stdscr.getch()

        if c is ord('s'):
            # We take off when the commander is created
            stdscr.addstr('Take off...\n')
            stdscr.refresh()
            with MotionCommander(scf) as mc:
                should_fly = True
                while should_fly:
                    # Get input
                    c = stdscr.getch()

                    # Manual control
                    if c is ord('q') or c is ord('Q'):
                        should_fly = False
                    elif c is ord('h'):
                        mc.stop()
                    elif c is ord('r'):
                        mc.start_right(0.5)
                    elif c is ord('l'):
                        mc.start_left(0.5)
                    elif c is ord('f'):
                        mc.start_forward(0.5)
                    elif c is ord('b'):
                        mc.start_back(0.5)

        stdscr.addstr('Land...\n')
        stdscr.refresh()

        time.sleep(5.0)


if __name__ == '__main__':
    curses.wrapper(main)