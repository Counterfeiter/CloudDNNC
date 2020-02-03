### written by Sebastian Foerster - https://github.com/Counterfeiter/, https://sebastianfoerster86.wordpress.com/
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import random, time
from DNNC import CloudDNNC

BACKENDLINK_DNNC = "http://dnncontroller.ddnss.de"

setPoint1 = 40.0
setPoint2 = 25.0

NUM_CONTROL_LOOPS = 250


def CreateOutputLoad():
    K = 6.931
    tau = 10  # s

    return signal.TransferFunction([K], [tau, 1.])


def CreateProcess(pt2=True):
    K = 0.8
    tau = 6.765
    D = 1.3
    dead_time = 2

    # (1) Transfer Function
    num = [K]
    if pt2:
        den = [tau ** 2, 2 * D * tau, 1.0]
    else:
        den = [tau * 4., 1.0]

    sys1 = signal.TransferFunction(num, den)

    return (sys1, dead_time)


def Simulate(ADD_LOAD_CHANGE=False, display_plot=True, display_backendcom=True, process_value_noise=0.0):
    # optional offset value for process value
    offset = 0.0
    sys, dead_time = CreateProcess()
    loaderror_sys = CreateOutputLoad()

    dead_time = int(dead_time)

    # set up initial inputs/outputs
    timearray = [0.0]
    timearray_load = [0.0]
    outputarray = [0.0]
    youtarray = [0.0 + offset]
    youtdtarray = [0.0 + offset]

    setPoint = setPoint1

    yout_last = 0.0 + offset
    yout_load = 0.0

    # create DNNC instance and get a session id
    cloudcontroller = CloudDNNC(BACKENDLINK_DNNC)

    # scale your process range - example temperature range from 0.0 to 60.0 deg C should be controlled
    cloudcontroller.setProcessValueRange(0.0, 60.0)
    # scale your actuator range - example - value with 100 steps from 0. to 100.
    cloudcontroller.setControlValueRange(0.0, 100.0)

    # loop in time steps
    for i in range(NUM_CONTROL_LOOPS):

        if not ADD_LOAD_CHANGE:
            yout_load = 0.0
        else:
            if i > int((NUM_CONTROL_LOOPS * 0.7)):
                (_, yout_load, _) = signal.lsim(loaderror_sys, np.ones(len(timearray_load)), timearray_load, X0=None,
                                                interp=False)
                timearray_load.append(timearray_load[-1] + 1.0)
                yout_load = np.atleast_1d(yout_load)[-1]

        # if the "old" actuator value has large step size - its not recommended to tell the DNNC about it
        # the real applied actuator/output value -> different behavior will be part of the process system
        dnnc = cloudcontroller(setPoint, yout_last)  # , outputarray[-1])
        time.sleep(0.2)  # be nice to my small little server
        if (display_backendcom):
            print(dnnc)

        output = dnnc["controlvalue"]

        # most actuators are limited in control values - round the actuator value here
        output_rounder = 1.0  # actuator steps
        output = round(output / output_rounder, 0) * output_rounder

        # setup new controller output array = process input array
        outputarray.append(output)
        timearray.append(timearray[-1] + 1.0)  # add time step

        # calculate new process output
        (_, yout, _) = signal.lsim(sys, outputarray, timearray, X0=None, interp=False)

        # add optional offset
        yout += offset

        # add delay
        youtdtarray.append(np.atleast_1d(yout)[-1])
        if dead_time <= 0:
            yout_last = youtdtarray[-1]
        else:
            if len(youtdtarray) >= dead_time:
                yout_last = youtdtarray[-dead_time]
            else:
                yout_last = youtdtarray[0]

        # add noise ?
        yout_last += random.random() * process_value_noise

        # after simulated output we have the "real" load change
        yout_last -= yout_load

        youtarray.append(yout_last)

        # change to second setpoint
        if i == int((NUM_CONTROL_LOOPS / 2)):
            setPoint = setPoint2

    # display plot as subplot
    if display_plot:
        ax1 = plt.subplot(111)
        ln2 = ax1.plot(timearray, outputarray, 'g-', label='control variable')
        ax1.set_ylabel('Output (% / %)')
        ax2 = ax1.twinx()
        ln1 = ax2.plot(timearray, youtarray, 'b', linewidth=1, label='process variable')
        ax2.plot([0, max(timearray)], [setPoint1, setPoint1], 'k:')
        ax2.plot([0, max(timearray)], [setPoint2, setPoint2], 'k:')
        ax2.set_xlim([0, max(timearray)])
        ax2.set_xlabel('t / timesteps')
        ax2.set_ylabel('Response (y)')
        lns = ln1 + ln2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc='center right')
        plt.xlabel('t / timesteps')
        # plt.legend(loc='center right')
        plt.show()


if __name__ == '__main__':
    print("Start control loop simulation - with CloudDNNC Backend:")
    print(BACKENDLINK_DNNC)

    Simulate()
    #Simulate(True)  # simulate with load change at 70% from max time steps
