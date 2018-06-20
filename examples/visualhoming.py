# Example usage of curses for control

import curses
import curses.panel
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger


URI = 'radio://0/80/250K'


def main(stdscr):
    cflib.crtp.init_drivers(enable_debug_driver=False)

    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
        lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
        lg_stab.add_variable('monocam.homingvector_x', 'float')
        lg_stab.add_variable('monocam.homingvector_y', 'float')

        curses.curs_set(False)
        stdscr.nodelay(True)
        stdscr.clear()
        stdscr.addstr(0, 0, 'Keyboard control demo\n', curses.A_REVERSE)
        stdscr.addstr("Press 's' to start and 'q' to quit...\n")
        stdscr.refresh()

        c = -1
        while c == -1:
            c = stdscr.getch()

        if c is ord('s'):
            # We take off when the commander is created
            stdscr.addstr('Take off...\n\n')
            stdscr.addstr('Controls: q (land and quit), h (halt), l r f b\n')
            stdscr.addstr('Snapshot: . (take), / (clear)\n')
            stdscr.refresh()
            with SyncLogger(scf, lg_stab) as logger:
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

                        elif c is ord('.'):
                            cf.param.set_value('visualhoming.make_snapshot', '1')
                        elif c is ord('/'):
                            cf.param.set_value('visualhoming.make_snapshot', '0')

                        # Print telemetry
                        for log_entry in logger:
                            timestamp = log_entry[0]
                            data = log_entry[1]
                            logconf_name = log_entry[2]

                            stdscr.addstr(10, 0, str(data['monocam.homingvector_x']))
                            stdscr.addstr(11, 0, str(data['monocam.homingvector_y']))
                            stdscr.refresh

                            break

        stdscr.addstr('Land...\n')
        stdscr.refresh()

        time.sleep(5.0)


if __name__ == '__main__':
    curses.wrapper(main)