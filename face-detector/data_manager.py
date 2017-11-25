import datetime

import cv2
import os
import time
import json
import numpy as np
import dlib
import skimage
import sys

import util

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('dlib-files/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('dlib-files/dlib_face_recognition_resnet_model_v1.dat')


class NoFaces(Exception):
    pass


class _Person(object):

    def __init__(self, id, data=None):
        self.faces = []
        self.vecs = []
        self.info = data or {}
        if self.info.get('id', id) != id:
            raise Exception('Read problem - IDs don\'t match')

    def save(self):
        os.makedirs('data/{}'.format(self.info['id']))
        with open('data/{}/info.json'.format(self.info['id']), 'w') as f:
            f.write(json.dumps(self.info))
        with open('data/{}/vecs.json'.format(self.info['id']), 'w') as f:
            f.write(json.dumps(list(map(list, self.vecs))))
        for idx, face in enumerate(self.faces):
            cv2.imwrite('data/{}/{}.jpg'.format(self.info['id'], idx), face[:, :, ::-1],
                        [int(cv2.IMWRITE_JPEG_QUALITY), 90])

    def detect_face(self, img, win):
        dets = detector(img, 1)

        if len(dets) == 0:
            raise NoFaces()

        largest_det = None
        l_sq = None
        for d in dets:
            win.add_overlay(d)
            sq = (d.right() - d.left()) * (d.top() - d.bottom())
            sq = abs(sq)
            if largest_det is None or sq > l_sq:
                largest_det = d
                l_sq = sq

        d = largest_det
        print("Detection: Left: {} Top: {} Right: {} Bottom: {}".format(
            d.left(), d.top(), d.right(), d.bottom()))
        # Get the landmarks/parts for the face in box d.
        shape = sp(img, d)
        # Draw the face landmarks on the screen so we can see what face is currently being processed.
        win.add_overlay(shape, color=dlib.rgb_pixel(0, 255, 0))
        face_descriptor = facerec.compute_face_descriptor(img, shape)

        self.faces.append(img)
        self.vecs.append(face_descriptor)


class DataManager(object):
    persons = None

    @classmethod
    def get_persons(cls):
        cls.persons = []
        ids = []
        for s in os.listdir('data'):
            try:
                id = int(s)
            except:
                pass
            else:
                ids.append(id)
        for id in sorted(ids):
            with open('data/{}/info.json'.format(id)) as f:
                cls.persons.append(_Person(id, json.loads(f.read())))
            p = cls.persons[-1]
            with open('data/{}/vecs.json'.format(id)) as f:
                p.vecs = json.loads(f.read())
            root = os.path.join('data', str(id))
            for face in os.listdir(root):
                if face.endswith('.jpg'):
                    p.faces.append(cv2.imread(os.path.join(root, face))[:, :, ::-1])

    @classmethod
    def get_person(cls, id):
        return cls.persons[id]

    @classmethod
    def get_data(cls):
        vecs = []
        labels = []
        for p in cls.persons:
            vecs += list(p.vecs)
            print(p.vecs)
            labels += [p.info['id']] * len(p.vecs)
        return np.array(vecs), labels

    @classmethod
    def add_person(cls):
        if cls.persons is None:
            mx = -1
            for person in os.listdir('data'):
                try:
                    id = int(person)
                    if id > mx:
                        mx = id
                except:
                    pass
            id = mx + 1
        else:
            id = len(cls.persons)
        name = sys.stdin.readline().strip()
        person = _Person(id, {'name': name})
        if cls.persons:
            cls.persons.append(person)
        vc = cv2.VideoCapture(0)

        rval = vc.isOpened()

        im_cnt = 0
        save_faces = False
        win = dlib.image_window()
        time_to_start = datetime.datetime.now() + datetime.timedelta(seconds=3)
        while rval and im_cnt < 10:
            rval, frame = vc.read()
            image = frame[:, :, ::-1]

            win.clear_overlay()
            win.set_image(image)
            if save_faces:
                try:
                    person.detect_face(image, win)
                except NoFaces:
                    pass
                else:
                    im_cnt += 1
            else:
                now = datetime.datetime.now()
                if now >= time_to_start:
                    save_faces = True
                    win.set_title('Saving...')
                else:
                    win.set_title('Seconds to start: {}'.format((time_to_start - now).total_seconds()))
        print('Faces: {}'.format(len(person.faces)))
        person.save()
