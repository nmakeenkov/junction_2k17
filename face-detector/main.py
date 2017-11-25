
# coding: utf-8

import cv2
import os
import numpy as np

import data_manager
import util


def predict(face_recognizer, test_img):
    img = test_img.copy()
    try:
        face, rect = data_manager.detect_face(img)
    except data_manager.NoFaces:
        print('No faces found')
        return

    label, confidence = face_recognizer.predict(face)
    print('...', confidence)
    # TODO: more info
    label_text = 'ID: {}'.format(label)
    
    util.draw_rectangle(img, rect)
    util.draw_text(img, label_text, rect[0], rect[1]-5)
    
    return img


if __name__ == '__main__':
    data_manager.DataManager.get_persons()
    faces, labels = data_manager.DataManager.get_data()

    print("Total faces: ", len(faces))
    print("Total labels: ", len(labels))


    # face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    # face_recognizer = cv2.face.EigenFaceRecognizer_create()
    face_recognizer = cv2.face.FisherFaceRecognizer_create()

    face_recognizer.train(faces, np.array(labels))

    for image__ in os.listdir('test-data'):
        test_img = cv2.imread("test-data/{}".format(image__))

        print(image__)
        predicted_img1 = predict(face_recognizer, test_img)

        import uuid
        if predicted_img1 is not None:
            cv2.imshow(str(uuid.uuid4()), predicted_img1)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cv2.destroyAllWindows()
