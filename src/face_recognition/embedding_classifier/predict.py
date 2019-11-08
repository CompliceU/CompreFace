from typing import List

import numpy as np

from src.face_recognition.dto.bounding_box import BoundingBox
from src.face_recognition.dto.cropped_face import CroppedFace
from src.face_recognition.dto.embedding import Embedding
from src.face_recognition.dto.face_prediction import FacePrediction
from src.face_recognition.embedding_calculator.calculator import calculate_embedding, CALCULATOR_VERSION
from src.face_recognition.embedding_classifier.train import CLASSIFIER_VERSION
from src.face_recognition.face_cropper.constants import FaceLimit
from src.face_recognition.face_cropper.cropper import crop_faces
from src.storage.dto.embedding_classifier import EmbeddingClassifier
from src.storage.storage import get_storage


def predict_from_embedding(classifier: EmbeddingClassifier, embedding: Embedding,
                           face_box: BoundingBox) -> FacePrediction:
    probabilities = classifier.model.predict_proba([embedding.array])[0]
    top_class = np.argsort(-probabilities)[0]
    return FacePrediction(face_name=classifier.class_2_face_name[top_class],
                          probability=probabilities[top_class], box=face_box)


def predict_from_image(img, limit: FaceLimit, api_key: str) -> List[FacePrediction]:
    classifier = get_storage(api_key).get_embedding_classifier(CLASSIFIER_VERSION, CALCULATOR_VERSION)

    def predict_from_cropped_face(face: CroppedFace):
        embedding = calculate_embedding(face.img)
        face_prediction = predict_from_embedding(classifier, embedding, face.box)
        return face_prediction

    return [predict_from_cropped_face(cropped_face) for cropped_face in crop_faces(img, limit)]
