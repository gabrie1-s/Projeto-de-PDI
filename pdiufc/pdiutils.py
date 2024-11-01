import numpy as np


def mixture_gaussian(norm_params, norm_weights):
    mixture_id = np.random.choice(len(norm_weights), size=1, replace=True, p=norm_weights)[0]
    return np.random.normal(*(norm_params[mixture_id]))


def overlay_images(background, image, pos_x, pos_y):
    bg_w, bg_h, _ = background.shape
    im_w, im_h, a = image.shape

    x_min, x_max = max(pos_y, 0), min(pos_y + im_w, bg_w)
    y_min, y_max = max(pos_x, 0), min(pos_x + im_h, bg_h)

    if x_max < 0 or x_min >= bg_w or y_max < 0 or y_min >= bg_h:
        return None

    x_im_min, x_im_max = x_min-pos_y, im_w-(pos_y+im_w-x_max)
    y_im_min, y_im_max = y_min-pos_x, im_h-(pos_x+im_h-y_max)

    if a == 4:
        alpha_im = image[x_im_min:x_im_max, y_im_min:y_im_max, 3] / 255.0
        alpha_bg = (1.0 - alpha_im)

        for c in range(0, 3):
            background[x_min:x_max, y_min:y_max, c] = alpha_im*image[x_im_min:x_im_max, y_im_min:y_im_max, c] \
                                                      + alpha_bg*background[x_min:x_max, y_min:y_max, c]
    else:
        background[x_min:x_max, y_min:y_max] = image[x_im_min:x_im_max, y_im_min:y_im_max]


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()
