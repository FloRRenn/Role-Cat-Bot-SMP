import os
import numpy as np
import onnxruntime
from .image_utils import load_images

class Classifier:
    nsfw_model = None

    def __init__(self):
        model_path = os.getcwd() + "/.Model/classifier_model.onnx"
        self.nsfw_model = onnxruntime.InferenceSession(model_path)

    def classify(self, image_paths = [], batch_size = 4, image_size = (256, 256), categories = ["unsafe", "safe"]):
        if not isinstance(image_paths, list):
            image_paths = [image_paths]

        loaded_images, loaded_image_paths = load_images(image_paths, image_size, image_names = image_paths)

        if not loaded_image_paths:
            return {}

        preds = []
        model_preds = []
        while len(loaded_images):
            _model_preds = self.nsfw_model.run(
                [self.nsfw_model.get_outputs()[0].name],
                {self.nsfw_model.get_inputs()[0].name: loaded_images[:batch_size]},
            )[0]
            
            model_preds.append(_model_preds)
            preds += np.argsort(_model_preds, axis = 1).tolist()
            loaded_images = loaded_images[batch_size:]

        probs = []
        for i, single_preds in enumerate(preds):
            single_probs = []
            for j, pred in enumerate(single_preds):
                single_probs.append(model_preds[int(i / batch_size)][int(i % batch_size)][pred])
                preds[i][j] = categories[pred]

            probs.append(single_probs)

        images_preds = {}

        for i, loaded_image_path in enumerate(loaded_image_paths):
            if not isinstance(loaded_image_path, str):
                loaded_image_path = i

            images_preds[loaded_image_path] = {}
            for _ in range(len(preds[i])):
                images_preds[loaded_image_path][preds[i][_]] = float(probs[i][_])

        return images_preds
