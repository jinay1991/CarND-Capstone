import os

import cv2
import numpy as np
import tensorflow as tf
import rospy

from styx_msgs.msg import TrafficLight

LABELS = [
    0,
    TrafficLight.RED,
    TrafficLight.YELLOW,
    TrafficLight.GREEN,
    TrafficLight.UNKNOWN
]

class TLClassifier(object):
    def __init__(self):
        model = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frozen_inference_graph.pb")
        assert os.path.exists(model), "model file not found at [%s]" % (model)

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
            class_idx = classes[i]

            if scores[i] > 0.50:
                return LABELS[int(class_idx)]

        return TrafficLight.UNKNOWN
