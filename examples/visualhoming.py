# Example usage of curses for control

import curses
import curses.panel
import time
import math as m

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger


URI = 'radio://0/80/250K'
# URI = 'radio://0/40/250K/E7E7E7E7EA'

VEL = 0.5


def main(stdscr):
    cflib.crtp.init_drivers(enable_debug_driver=False)

    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
        lg_stab = LogConfig(name='Homing', period_in_ms=10)
        lg_stab.add_variable('monocam.homingvector_x', 'float')
        lg_stab.add_variable('monocam.homingvector_y', 'float')

        curses.curs_set(False)
        stdscr.nodelay(True)
        stdscr.clear()
        stdscr.addstr(0, 0, 'Keyboard control demo\n', curses.A_REVERSE)
        stdscr.addstr('Controls: q (land and quit), h (halt), l r f b, z (home)\n')
        stdscr.addstr('Snapshot: . (take), / (clear)\n')
        stdscr.addstr("Press 's' to start and 'q' to quit...\n")
        stdscr.refresh()

        c = -1
        while c == -1:
            c = stdscr.getch()

        if c is ord('s'):
            # We take off when the commander is created
            stdscr.addstr('Take off...\n\n')
            stdscr.refresh()
            with SyncLogger(scf, lg_stab) as logger:
                with MotionCommander(scf) as mc:
                    homing = False
                    should_fly = True
                    while should_fly:
                        # Get homing vector
                        hx = 0.0
                        hy = 0.0
                        for log_entry in logger:
                            timestamp = log_entry[0]
                            data = log_entry[1]
                            logconf_name = log_entry[2]
                            hx = -data['monocam.homingvector_x'] # TODO fix
                            hy = data['monocam.homingvector_y']
                            stdscr.addstr(10, 0, '{:+6.2f}'.format(hx))
                            stdscr.addstr(11, 0, '{:+6.2f}'.format(hy))
                            stdscr.refresh
                            break

                        # Get input
                        c = stdscr.getch()

                        # Manual control
                        if c is ord('q') or c is ord('Q'):
                            should_fly = False
                        elif c is ord('h') or c is ord('H'):
                            mc.stop()
                        elif c is ord('r'):
                            mc.start_right(VEL)
                        elif c is ord('l'):
                            mc.start_left(VEL)
                        elif c is ord('f'):
                            mc.start_forward(VEL)
                        elif c is ord('b'):
                            mc.start_back(VEL)

                        elif c is ord('.'):
                            cf.param.set_value('visualhoming.make_snapshot', '1')
                        elif c is ord('/'):
                            cf.param.set_value('visualhoming.make_snapshot', '0')

                        if c is ord('z'):
                            homing = True
                            stdscr.addstr(9, 0, 'HOMING', curses.A_BLINK + curses.A_BOLD)
                            stdscr.refresh()
                        elif c is not -1:
                            homing = False
                            stdscr.move(9, 0)
                            stdscr.clrtoeol()
                            stdscr.refresh()


                        if homing:
                            mag = m.sqrt(hx*hx + hy*hy)
                            if mag < 0.02:
                                mc.stop()
                            else:
                                hx = hx / mag
                                hy = hy / mag
                                if mag > 0.10:
                                    mag = 0.10
                                vx = hx * mag * 10 * VEL
                                vy = hy * mag * 10 * VEL
                                mc.start_linear_motion(vx, vy, 0.0)



        stdscr.addstr('Landing...\n')
        stdscr.refresh()

        time.sleep(2.0)


if __name__ == '__main__':
    curses.wrapper(main)