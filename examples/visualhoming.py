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


# URI = 'radio://0/80/250K'
URI = 'radio://0/40/250K/E7E7E7E7EA'
# URI = 'radio://0/60/250K/E7E7E7E7EB'

VEL = 0.5


def main(stdscr):
    cflib.crtp.init_drivers(enable_debug_driver=False)

    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
        lg_stab = LogConfig(name='Homing', period_in_ms=10)
        lg_stab.add_variable('monocam.homingvector_x', 'float')
        lg_stab.add_variable('monocam.homingvector_y', 'float')
        lg_stab.add_variable('stabilizer.thrust', 'float')
        # lg_stab.add_variable('pm.state', 'uint8_t')

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
                # # Check drone is not charging
                # is_charging = True
                # while is_charging:
                #     for log_entry in logger:
                #         data = log_entry[1]
                #         is_charging = data['pm.state']
                #         if is_charging:
                #             stdscr.addstr(10, 0, 'Drone {} is still charging!\n'.format(URI), curses.A_REVERSE)
                #             stdscr.refresh()
                # stdscr.move(10, 0)
                # stdscr.clrtoeol()
                # stdscr.refresh()

                with MotionCommander(scf, default_height=0.8) as mc:
                    should_fly = True
                    while should_fly:
                        # Get homing vector
                        for log_entry in logger:
                            timestamp = log_entry[0]
                            data = log_entry[1]
                            logconf_name = log_entry[2]
                            hx = data['monocam.homingvector_x']
                            hy = data['monocam.homingvector_y'] # Note: FLU frame
                            stdscr.addstr(10, 0, '{:+6.2f}'.format(hx))
                            stdscr.addstr(11, 0, '{:+6.2f}'.format(hy))
                            stdscr.addstr(13, 0, 'Thrust: {:+8.0f}'.format(data['stabilizer.thrust']))
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
                            cf.param.set_value('visualhoming.follow_vector', '1')
                            stdscr.addstr(9, 0, 'HOMING', curses.A_BLINK + curses.A_BOLD)
                            stdscr.refresh()
                        elif c is not -1:
                            cf.param.set_value('visualhoming.follow_vector', '0')
                            stdscr.move(9, 0)
                            stdscr.clrtoeol()
                            stdscr.refresh()

        stdscr.addstr('Landing...\n')
        stdscr.refresh()

        time.sleep(2.0)


if __name__ == '__main__':
    curses.wrapper(main)