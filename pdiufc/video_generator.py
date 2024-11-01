import os
import cv2
import imutils
import numpy as np
import skimage
import pdiutils
from datetime import datetime
import random


#####################################################################################################################%#
################################################## SYSTEM PARAMETERS ##################################################
#######################################################################################################################

# Camera Information
fov = 90                            # field of view (deg)
width = 1280                        # camera image width (px)
height = 720                        # camera image height (px)
dist_camera_to_conveyor = 50        # distance from camera to conveyor belt (cm)

# Object Dimensions
object_width = [4, 8, 10]         # object width (cm)
object_height = 25                # object height (cm)

# System Information
conveyor_speed = 4                 # conveyor speed (cm/s)
objects_per_column = 2              # quantity of objects in each column
h_dist_between_objects = 4          # horizontal distance between objects (cm)
object_name = 'rasgo'              # object image name (image must be in folder /images/object/)
object_name2 = 'mancha'             # object image name (image must be in folder /images/object/)
object_name3 = 'mancha2'             # object image name (image must be in folder /images/object/)
object_name4 = 'mancha3'             # object image name (image must be in folder /images/object/)
object_name6 = 'furo'             # object image name (image must be in folder /images/object/)
object_name7 = 'transparente'             # object image name (image must be in folder /images/object/)
background_name = 'tecido'             # background image name (image must be in folder /images/background/)

# Video output feature
fps = 30                            # frames per second
video_duration = 90                # video duration (s)

# Noise Management
# brightness = 0
noise_type = ''                     # gaussian, poisson, salt, pepper, s&p, speckle or empty string for no noise
noise_object_position = 0.3         # x: evenly distributed random value in the range [-x cm, x cm]
noise_object_size = 0.1             # x: evenly distributed random value in the range [-x cm, x cm]
norm_params = np.array([[-20, 9], [0, 4], [20, 9]])   # noise parameters for rotation
norm_weights = [1.0/16.0, 14.0/16.0, 1.0/16.0]        # noise parameters for rotation
flip_probability = [1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 1/80, 60/80]               # probability of the object image being inverted

#######################################################################################################################
#######################################################################################################################
#####################################################################################################################%#

# System Internal Variables
_conveyor_width = int(round(2 * dist_camera_to_conveyor * np.tan((np.pi / 180 * fov) / 2)))                 # cm
_pixels_per_centimeter = round(width / _conveyor_width)                                                     # px/cm
_conveyor_height = round(height / _pixels_per_centimeter)                                                   # cm

_object_width_px = [round(object_width[0] * _pixels_per_centimeter), round(object_width[1] * _pixels_per_centimeter),
                    round(object_width[2] * _pixels_per_centimeter)]  #px

_object_height_px = round(object_height * _pixels_per_centimeter)                                           # px
_conveyor_speed_px = conveyor_speed * _pixels_per_centimeter                                                # px/s
_h_distance_between_columns = (object_width[1] + h_dist_between_objects) * _pixels_per_centimeter              # px
_v_distance_between_lines = int(np.ceil((height + _object_height_px) / (objects_per_column + 1)))           # px
_line_positions = range(_v_distance_between_lines - _object_height_px, height, _v_distance_between_lines)   # px's
_pixels_shift_per_frame = _conveyor_speed_px / fps                                                          # px/frame
_half_object_width_px = round(_object_width_px[1] / 2)                                                         # px
_half_object_height_px = round(_object_height_px / 2)                                                       # px
_noise_position = noise_object_position * _pixels_per_centimeter                                            # px
_noise_size = noise_object_size * _pixels_per_centimeter                                                    # px
_object_characteristics = \
    np.zeros((1, len(_line_positions), 6))  # pos_noise_x, pos_noise_y, size_noise_x, size_noise_y, rotation, idx_flip

# Prepare output video
fourcc = cv2.VideoWriter_fourcc(*'MP42')
os.makedirs("../results", exist_ok=True)
_output_video_name = '../results/video_' + datetime.now().strftime("%Y%m%d%H%M%S")
video = cv2.VideoWriter(_output_video_name + '.avi', fourcc, float(fps), (width, height))

# Get images
_bg_pattern = cv2.imread('../images/background/' + background_name + '.jpg')
_object = cv2.imread('../images/object/' + object_name + '.png', cv2.IMREAD_UNCHANGED)
_object2 = cv2.imread('../images/object/' + object_name2 + '.png', cv2.IMREAD_UNCHANGED)
_object3 = cv2.imread('../images/object/' + object_name3 + '.png', cv2.IMREAD_UNCHANGED)
_object4 = cv2.imread('../images/object/' + object_name4 + '.png', cv2.IMREAD_UNCHANGED)
_object6 = cv2.imread('../images/object/' + object_name6 + '.png', cv2.IMREAD_UNCHANGED)
_object7 = cv2.imread('../images/object/' + object_name7 + '.png', cv2.IMREAD_UNCHANGED)

_object_resized = cv2.resize(_object, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)
_object_resized2 = cv2.resize(_object, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)
_object_resized3 = cv2.resize(_object, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)

_object2_resized = cv2.resize(_object2, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)
_object2_resized2 = cv2.resize(_object2, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)
_object2_resized3 = cv2.resize(_object2, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)

_object3_resized = cv2.resize(_object3, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)
_object3_resized2 = cv2.resize(_object3, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)
_object3_resized3 = cv2.resize(_object3, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)

_object4_resized = cv2.resize(_object4, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)
_object4_resized2 = cv2.resize(_object4, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)
_object4_resized3 = cv2.resize(_object4, (random.choice(_object_width_px), _object_height_px), interpolation=cv2.INTER_AREA)

aux6 = random.choice([3,4])
_object6_resized = cv2.resize(_object6, (aux6, aux6), interpolation=cv2.INTER_AREA)
aux6 = random.choice([3,4])
_object6_resized2 = cv2.resize(_object6, (aux6, aux6), interpolation=cv2.INTER_AREA)
aux6 = random.choice([3,4])
_object6_resized3 = cv2.resize(_object6, (aux6, aux6), interpolation=cv2.INTER_AREA)

_object_variations = [
    _object,
    cv2.flip(_object_resized, 0),
    cv2.flip(_object_resized2, 1),
    cv2.flip(_object_resized3, -1),
    _object2,
    cv2.flip(_object2_resized, 0),
    cv2.flip(_object2_resized2, 1),
    cv2.flip(_object2_resized3, -1),
    _object3,
    cv2.flip(_object3_resized, 0),
    cv2.flip(_object3_resized2, 1),
    cv2.flip(_object3_resized3, -1),
    _object4,
    cv2.flip(_object4_resized, 0),
    cv2.flip(_object4_resized2, 1),
    cv2.flip(_object4_resized3, -1),
    _object6,
    cv2.flip(_object6_resized, 0),
    cv2.flip(_object6_resized2, 1),
    cv2.flip(_object6_resized3, -1),
    _object7
]

def add_objects(background, x_pos, bg_limit):
    obj_w = _h_distance_between_columns
    w = min(bg_limit, background.shape[1])

    for i, x in enumerate(range(x_pos - obj_w, w, obj_w)):
        for j, y in enumerate(_line_positions):
            if all(_object_characteristics[i, j, :] == np.zeros(len(_object_characteristics[i, j, :]))):
                _object_characteristics[i, j, 0] = round(np.random.uniform(-_noise_position, _noise_position, 1)[0])
                _object_characteristics[i, j, 1] = round(np.random.uniform(-_noise_position, _noise_position, 1)[0])
                _object_characteristics[i, j, 2] = round(np.random.uniform(-_noise_size, _noise_size, 1)[0])
                _object_characteristics[i, j, 3] = round(np.random.uniform(-_noise_size, _noise_size, 1)[0])
                _object_characteristics[i, j, 4] = pdiutils.mixture_gaussian(norm_params, norm_weights)
                _object_characteristics[i, j, 5] = np.random.choice(range(len(_object_variations)), p=flip_probability)

            chosen_object = _object_variations[int(_object_characteristics[i, j, 5])]
            object_ = chosen_object

            obj_rotated = imutils.rotate_bound(object_, _object_characteristics[i, j, 4])
            dx = round((obj_rotated.shape[1] - object_.shape[1]) / 2.0)
            dy = round((obj_rotated.shape[0] - object_.shape[0]) / 2.0)

            x = x - dx + int(_object_characteristics[i, j, 0])
            y = y - dy + int(_object_characteristics[i, j, 1])

            pdiutils.overlay_images(background, obj_rotated, x, y)


def add_background(background, x_pos):
    w, h, _ = background.shape
    bgp_w, bgp_h, _ = _bg_pattern.shape

    for i in range(x_pos-bgp_h, h, bgp_h):
        for j in range(0, w, bgp_w):
            pdiutils.overlay_images(background, _bg_pattern, i, j)


def save_parameters():
    save_current_line = False
    with open(_output_video_name + '.txt', 'a') as f1:
        for line in open('video_generator.py'):
            if '#%#' in line and not save_current_line:
                save_current_line = True
            elif '#%#' in line and save_current_line:
                f1.write(line)
                break
            if save_current_line:
                f1.write(line)


# Auxiliary variables
_pixels_count = 0
_pixels_accumulator = 0.0
_background_shift = 0
_objects_shift = 0

save_parameters()

# Loop to create each video frame
for f in range(fps * video_duration):
    # Show progress bar on console
    pdiutils.print_progress_bar(f, fps * video_duration - 1, prefix='Progress:', suffix='Complete', length=70)

    # Calculate objects shift in current frame
    _pixels_accumulator += _pixels_shift_per_frame
    _iteration_shift = int(np.ceil(_pixels_accumulator))
    _pixels_accumulator -= _iteration_shift
    _pixels_count += _iteration_shift

    # Structure management that stores characteristics of objects in the image
    if _objects_shift + _iteration_shift >= _h_distance_between_columns:
        if _pixels_count >= width + _h_distance_between_columns:
            _object_characteristics = np.delete(_object_characteristics, -1, 0)
        _object_characteristics = np.insert(_object_characteristics, 0, 0, axis=0)

    # Create base frame
    frame = np.zeros([height, width, 3], dtype=np.uint8)
    frame.fill(255)

    # Add background to base frame
    _background_shift = (_background_shift + _iteration_shift) % _bg_pattern.shape[1]
    add_background(frame, _background_shift)

    # Add object grid to base frame
    _objects_shift = (_objects_shift + _iteration_shift) % _h_distance_between_columns
    add_objects(frame, _objects_shift, _pixels_count)

    # Add noise to frame (too slow)
    if noise_type:
        noisy = skimage.util.random_noise(frame/255.0, mode=noise_type)
        frame = cv2.normalize(noisy, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    video.write(frame)

video.release()
