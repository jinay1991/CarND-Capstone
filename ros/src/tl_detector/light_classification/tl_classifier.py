import os

import cv2
import numpy as np
import tensorflow as tf

from styx_msgs.msg import TrafficLight

LABELS = [
    TrafficLight.UNKNOWN,
    TrafficLight.RED,
    TrafficLight.YELLOW,
    TrafficLight.GREEN
]

class TLClassifier(object):
    def __init__(self):
        model = os.path.join(os.path.abspath(os.path.curpath), "ssd_mobilenet_v2_coco.pb")

        # Read graph
        graph = tf.Graph()
        graph_def = tf.GraphDef()
        with open(model, 'rb') as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)

        # set tensor holders
        self.image_tensor = graph.get_tensor_by_name("import/image_tensor:0")
        self.detection_boxes = graph.get_tensor_by_name("import/detection_boxes:0")
        self.detection_scores = graph.get_tensor_by_name("import/detection_scores:0")
        self.detection_classes = graph.get_tensor_by_name("import/detection_classes:0")

        # Load graph
        self.session = tf.Session(graph=graph)

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        # preprocess image
        image_ = cv2.resize(image, (300, 300))
        image_ = cv2.cvtColor(image_, cv2.COLOR_BGR2RGB)
        image_ = image_.astype(np.float32)

        # traffic light detection
        classes, scores, boxes = self.session.run([self.detection_classes, self.detection_scores, self.detection_boxes],
                                                  feed_dict={self.image_tensor: np.expand_dims(image_, axis=0)})
        classes = np.squeeze(classes)
        scores = np.squeeze(scores)
        boxes = np.squeeze(boxes)

        # identify type of signal (RED/GREEN/YELLOW)
        for i in range(boxes.shape[0]):
            class_idx = classes[i] - 1

            if scores[i] > 0.30:
                if class_idx in LABELS[1:]:
                    return class_idx

        return TrafficLight.UNKNOWN
