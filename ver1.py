import serial
import time

def build_command(
    a_val=0,
    b_throttle=0,
    c_val=0,
    d_steering=50,
    e_left_indicator=0,
    f_horn=0,
    g_light=0,
    h_right_indicator=0,
    i_brake=0,
    j_reverse=0
):
    """
    Build the control command string in the format:
    *A{a_val}B{b_throttle}C{c_val}D{d_steering}E{e_left_indicator}F{f_horn}G{g_light}H{h_right_indicator}I{i_brake}J{j_reverse}#
    """
    command = (
        f"*A{a_val}"
        f"B{b_throttle}"
        f"C{c_val}"
        f"D{d_steering}"
        f"E{e_left_indicator}"
        f"F{f_horn}"
        f"G{g_light}"
        f"H{h_right_indicator}"
        f"I{i_brake}"
        f"J{j_reverse}#"
    )
    return command

def print_help():
    """Print available commands to control the cart."""
    print("\nAvailable commands:")
    print("  th <value>      : Set throttle (e.g. 'th 70') -- will first send 'th 50' then go to desired value.")
    print("  st <value>      : Set steering (e.g. 'st 40')")
    print("  li              : Toggle left indicator")
    print("  ri              : Toggle right indicator")
    print("  lights          : Toggle lights")
    print("  horn            : Toggle horn")
    print("  brake           : Toggle brake")
    print("  reverse         : Toggle reverse")
    print("  show            : Show current state")
    print("  help            : Show this help menu")
    print("  quit / q        : Exit the console\n")

port_name = '/dev/ttyUSB1'  # Change this if needed
ser = serial.Serial(
    port=port_name,
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1  # Read timeout
)
a_val = 0
b_throttle = 0
c_val = 0
d_steering = 50
e_left_indicator = 0
f_horn = 0
g_light = 0
h_right_indicator = 0
i_brake = 0
j_reverse = 0
def main():
    # -- Initial Values --
    # Start with throttle=0, steering=50, everything else off

    # Configure serial port

    if ser.is_open:
        print(f"\n[INFO] Serial port {port_name} opened successfully at 9600,8N1.")
    else:
        print(f"\n[ERROR] Could not open serial port {port_name}. Check the connection.")
        return

    def send_state():
        """
        Build and send the current state to the controller, then read/print any response.
        """
        cmd = build_command(
            a_val,
            b_throttle,
            c_val,
            d_steering,
            e_left_indicator,
            f_horn,
            g_light,
            h_right_indicator,
            i_brake,
            j_reverse
        )
        # Send command
        ser.write(cmd.encode())

        # Small delay to let the controller process and respond
        time.sleep(0.1)

        # Read all available lines from the controller
        while True:
            line = ser.readline()
            if not line:
                break
            # Decode and print
            print(f"[RESPONSE] {line.decode(errors='replace').rstrip()}")

    # Immediately send the initial (idle) state once on startup
    send_state()

    # Print help on startup
    print_help()

    try:
        while True:
            user_input = input("Enter command: ").strip().lower()
            if not user_input:
                continue

            parts = user_input.split()
            cmd = parts[0]

            if cmd in ["quit", "q"]:
                print("[INFO] Exiting console.")
                break

            elif cmd == "help":
                print_help()

            elif cmd == "show":
                print("\nCurrent state:")
                print(f"  Throttle:       {b_throttle}")
                print(f"  Steering:       {d_steering}")
                print(f"  Left Indicator: {e_left_indicator}")
                print(f"  Right Indicator:{h_right_indicator}")
                print(f"  Lights:         {g_light}")
                print(f"  Horn:           {f_horn}")
                print(f"  Brake:          {i_brake}")
                print(f"  Reverse:        {j_reverse}\n")

            elif cmd == "th":  # throttle
                if len(parts) == 2:
                    try:
                        value = int(parts[1])
                        # 1) First send throttle=50, unless we are *already* at 50
                        if b_throttle != 50:
                            b_throttle = 50
                            print("[INFO] Setting throttle to 50 first...")
                            send_state()

                        # 2) Now set throttle to the user-requested value
                        b_throttle = max(0, min(value, 100))
                        print(f"[INFO] Throttle set to {b_throttle}")
                        send_state()

                    except ValueError:
                        print("[ERROR] Invalid throttle value. Must be an integer.")
                else:
                    print("[ERROR] Usage: th <value> (0 to 100)")

            elif cmd == "st":  # steering
                if len(parts) == 2:
                    try:
                        value = int(parts[1])
                        d_steering = max(0, min(value, 100))
                        print(f"[INFO] Steering set to {d_steering}")
                        send_state()
                    except ValueError:
                        print("[ERROR] Invalid steering value. Must be an integer.")
                else:
                    print("[ERROR] Usage: st <value> (0 to 100)")

            elif cmd == "li":  # toggle left indicator
                e_left_indicator = 1 - e_left_indicator
                print(f"[INFO] Left Indicator {'ON' if e_left_indicator == 1 else 'OFF'}")
                send_state()

            elif cmd == "ri":  # toggle right indicator
                h_right_indicator = 1 - h_right_indicator
                print(f"[INFO] Right Indicator {'ON' if h_right_indicator == 1 else 'OFF'}")
                send_state()

            elif cmd == "lights":
                g_light = 1 - g_light
                print(f"[INFO] Lights {'ON' if g_light == 1 else 'OFF'}")
                send_state()

            elif cmd == "horn":
                f_horn = 1 - f_horn
                print(f"[INFO] Horn {'ON' if f_horn == 1 else 'OFF'}")
                send_state()

            elif cmd == "brake":
                i_brake = 1 - i_brake
                print(f"[INFO] Brake {'ON' if i_brake == 1 else 'OFF'}")
                send_state()

            elif cmd == "reverse":
                j_reverse = 1 - j_reverse
                print(f"[INFO] Reverse {'ON' if j_reverse == 1 else 'OFF'}")
                send_state()

            else:
                print("[ERROR] Unknown command. Type 'help' for a list of commands.")

    except KeyboardInterrupt:
        print("\n[INFO] User interrupted the script.")
    finally:
        # This will publish 0 to the cart as soon as the script is closed
        b_throttle = 0
        d_steering = 50
        send_state()
        print("Publishing zero velocity and steering.")

        # Close the serial port properly
        ser.close()
        print("[INFO] Serial port closed.")

if __name__ == "__main__":
    main()
