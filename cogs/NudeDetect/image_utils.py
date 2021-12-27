import cv2
import logging
import numpy as np

from PIL import Image as pil_image

if pil_image is not None:
    _PIL_INTERPOLATION_METHODS = {
        "nearest": pil_image.NEAREST,
        "bilinear": pil_image.BILINEAR,
        "bicubic": pil_image.BICUBIC,
    }
    
    if hasattr(pil_image, "HAMMING"):
        _PIL_INTERPOLATION_METHODS["hamming"] = pil_image.HAMMING
        
    if hasattr(pil_image, "BOX"):
        _PIL_INTERPOLATION_METHODS["box"] = pil_image.BOX
        
    if hasattr(pil_image, "LANCZOS"):
        _PIL_INTERPOLATION_METHODS["lanczos"] = pil_image.LANCZOS


def load_img(path, grayscale = False, color_mode = "rgb", target_size = None, interpolation = "nearest"):
    if grayscale is True:
        logging.warn("grayscale is deprecated. Please use " 'color_mode = "grayscale"')
        color_mode = "grayscale"
        
    if pil_image is None:
        raise ImportError("Could not import PIL.Image. " "The use of `load_img` requires PIL.")

    if isinstance(path, type("")):
        img = pil_image.open(path)
        
    else:
        path = cv2.cvtColor(path, cv2.COLOR_BGR2RGB)
        img = pil_image.fromarray(path)

    if color_mode == "grayscale":
        if img.mode != "L":
            img = img.convert("L")
            
    elif color_mode == "rgba":
        if img.mode != "RGBA":
            img = img.convert("RGBA")
            
    elif color_mode == "rgb":
        if img.mode != "RGB":
            img = img.convert("RGB")
            
    else:
        raise ValueError('color_mode must be "grayscale", "rgb", or "rgba"')
    
    if target_size is not None:
        width_height_tuple = (target_size[1], target_size[0])
        
        if img.size != width_height_tuple:
            if interpolation not in _PIL_INTERPOLATION_METHODS:
                raise ValueError(
                    "Invalid interpolation method {} specified. Supported "
                    "methods are {}".format(
                        interpolation, ", ".join(_PIL_INTERPOLATION_METHODS.keys())
                    )
                )
                
            resample = _PIL_INTERPOLATION_METHODS[interpolation]
            img = img.resize(width_height_tuple, resample)
            
    return img


def img_to_array(img, data_format = "channels_last", dtype = "float32"):
    if data_format not in {"channels_first", "channels_last"}:
        raise ValueError("Unknown data_format: %s" % data_format)

    x = np.asarray(img, dtype = dtype)
    if len(x.shape) == 3:
        if data_format == "channels_first":
            x = x.transpose(2, 0, 1)
            
    elif len(x.shape) == 2:
        if data_format == "channels_first":
            x = x.reshape((1, x.shape[0], x.shape[1]))
        else:
            x = x.reshape((x.shape[0], x.shape[1], 1))
            
    else:
        raise ValueError("Unsupported image shape: %s" % (x.shape,))
    return x


def load_images(image_paths, image_size, image_names):
    loaded_images = []
    loaded_image_paths = []

    for i, img_path in enumerate(image_paths):
        try:
            image = load_img(img_path, target_size = image_size)
            image = img_to_array(image)
            image /= 255
            loaded_images.append(image)
            loaded_image_paths.append(image_names[i])
            
        except Exception as ex:
            logging.exception(f"Error reading {img_path} {ex}", exc_info = True)

    return np.asarray(loaded_images), loaded_image_paths
