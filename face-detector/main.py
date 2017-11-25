
# coding: utf-8
import datetime

import cv2
import os

import dlib
import numpy as np
import uuid

import skimage

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
    vecs, labels = data_manager.DataManager.get_data()

    vc = cv2.VideoCapture(0)

    rval = vc.isOpened()

    im_cnt = 0
    save_faces = False
    win = dlib.image_window()
    person = data_manager._Person(-1)  # fake person
    current_text = None
    fails_cnt = 0
    while rval:
        rval, frame = vc.read()
        image = frame[:, :, ::-1]
        if current_text is not None:
            util.draw_text(frame, current_text, 210, 40)
            win.set_image(frame[:, :, ::-1])
        else:
            win.set_image(image)

        win.clear_overlay()
        try:
            person.detect_face(image, win)
        except data_manager.NoFaces:
            fails_cnt += 1
            if fails_cnt > 3:
                current_text = None
        else:
            fails_cnt = 0
            vec = person.vecs[-1]
            best_dist = None
            best_idx = -1
            for idx, v in enumerate(vecs):
                dist = np.linalg.norm(vec - v)
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            if best_dist > .5:
                current_text = 'STRANGER'
            else:
                p = data_manager.DataManager.get_person(labels[best_idx])
                current_text = 'Person {}: {}'.format(p.info['id'], p.info['data'].get('name', 'Unknown'))
                print(best_dist)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cv2.destroyAllWindows()
