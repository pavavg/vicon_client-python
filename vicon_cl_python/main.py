import time
import threading
import argparse
import numpy as np
#from scipy.spatial.transform import Rotation as R

from vicon_client import ViconObject, ViconClient


# Function that reads the message and updates the vicon object non-stop
def read_vicon(client, item):
    global current_object
    global vicon_object

    while True:
        global stop_thread

        message = client.read_message()
        current_object = ViconObject(message)

        if item == current_object.name or item == '':
            vicon_object = current_object

        if stop_thread:
            break


# Perform transformation from marker to camera (marker -> camera)
def transformate(vic_obj):
    dx = -0.006
    dy = 0.095
    dz = 0.026

    translation = vic_obj.translation
    rot = vic_obj.rotation
    rotation_mat = np.matrix([
        [rot[0], rot[1], rot[2]],
        [rot[3], rot[4], rot[5]],
        [rot[6], rot[7], rot[8]]
    ])
    input_position = np.c_[rotation_mat, translation]
    input_position = np.r_[input_position, [[0., 0., 0., 1.]]]  # 4x4 transformation matrix

    shift_matrix = np.matrix([  # Position shift matrix
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ])

    input_position = input_position.astype(float)
    shift_matrix = shift_matrix.astype(float)
    output_pos = np.dot(input_position, shift_matrix)

    new_translation = [output_pos[0, 3], output_pos[1, 3], output_pos[2, 3]]

    new_rotation = []
    for i in range(3):
        for j in range(3):
            new_rotation += [output_pos[i, j]]

    return new_translation, new_rotation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-type', '--type', help='Type. Demo (demo) or Button Press (bpress). \n This feature requires root access.', default='demo', choices=['demo', 'bpress'])
    parser.add_argument('-item', '--item', help='Item. The marker you want to track.', default='')
    args = parser.parse_args()
    type = args.type
    item = args.item

    # Connect to Vicon
    client = ViconClient("127.0.0.1", 51602)
    print('Connecting.....')
    while True:
        try:
            client.connect()
            print('Connection established')
            break
        except:
            time.sleep(1)
            print('Could not connect. Retrying...')
            continue

    global stop_thread  # Flag to stop thread
    stop_thread = False

    # Run thread that reads vicon messages non-stop
    #item = "marker04"
    th = threading.Thread(target=read_vicon, args=(client, item, ))
    th.start()
    time.sleep(0.1)  # Important, because the first message most probably will be incomplete.

    transform = False
    if type == 'demo':
        for i in range(100):
            time.sleep(0.1)

            if transform:
                new_tr, new_rot = transformate(vicon_object)
                properties = [vicon_object.name] + new_tr + new_rot
                print(properties)
            else:
                print(vicon_object.get_properties())
    else:
        import keyboard
        print('Press SPACE to print message. ESC for exit.')
        while True:
            if keyboard.is_pressed('space'):
                time.sleep(0.3)

                if transform:
                    new_tr, new_rot = transformate(vicon_object)
                    properties = [vicon_object.name] + new_tr + new_rot
                    print(properties)
                else:
                    print(vicon_object.get_properties())

            if keyboard.is_pressed('esc'):
                break

    stop_thread = True


if __name__ == "__main__":
    main()
