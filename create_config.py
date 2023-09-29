import sys

from load_dataset import *
from model import *

# image resolution
HD = (1080, 1920)
HD_4_3 = (1080, 1440)

resize = '--resize' in sys.argv
grey = '--grey' in sys.argv

if __name__ == '__main__':
    '''
    :params
    --resize [(width, height)] | HD = (1080, 1920), HD_4_3 = (1080, 1440) | HD_4_3 is used if not specified
    --grey [bool] | Use greyscale images
    '''
    if resize:
        if 'HD' in sys.argv:
            scale=HD
        else:
            scale=HD_4_3
    
    dataset_config = Settings(scale, grey)
    dataset_config.resize()

    if grey:
        dataset_config.rgb_to_greyscale()

    # dataset_config.parse_ids()
    # dataset_config.create_binfiles()
    x, ids = dataset_config.read_binfiles()
    print(x)
    # dataset_config.load_images()