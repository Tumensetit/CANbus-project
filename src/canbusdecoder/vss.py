# Experimental DBC to VSS signal conversion.
# Notes:
## This mapping is DBC specific. MD5sum of the the expected file:
## 95e68160afa70e21a888fa655578a73d  data/toyota_rav4_hybrid_2017_pt_generated.dbc

## Many DBC messages can have the same signal name.
## This only maps signals, so it might map the signal name to wrong message

def convertDataToVss(input_signals):
    dbc_signal_to_vss_signals = {
        "YAW_RATE": "Vehicle.AngularVelocity.Yaw",
        "STEERING_TORQUE": "Vehicle.MotionManagement.Steering.SteeringWheel.Torque",
        "SPEED": "Vehicle.Speed",
        "CRUISE_ACTIVE": "ADAS.ADAS.CruiseControl.IsEnabled",
        "ODOMETER": "Vehicle.TraveledDistance",
        "DOOR_OPEN_FL": "Cabin.Cabin.Door.Row1.DriverSide.IsOpen",
        "DOOR_OPEN_RL": "Cabin.Cabin.Door.Row2.DriverSide",
        "DOOR_OPEN_RR": "Cabin.Cabin.Door.Row1.PassengerSide.IsOpen",
        "DOOR_OPEN_FR": "Cabin.Cabin.Door.Row2.PassengerSide.IsOpen"
    }

    mapped_signals = {}

    for signal, value in input_signals.items():
        if signal in dbc_signal_to_vss_signals:
            mapped_signals[dbc_signal_to_vss_signals[signal]] = value
        else:
            mapped_signals[signal] = value

    return mapped_signals