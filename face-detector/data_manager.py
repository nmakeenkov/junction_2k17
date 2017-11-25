import cv2
import os
import time
import json
import numpy as np

import util


class NoFaces(Exception):
    pass


def detect_face(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier('opencv-files/lbpcascade_frontalface.xml')

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    if len(faces) == 0:
        raise NoFaces()

    (x, y, w, h) = faces[0]

    return cv2.resize(gray[y:y + w, x:x + h], (500, 500)), faces[0]


class _Person(object):

    def __init__(self, id, data=None):
        self.faces = []
        self.info = {
            'id': id,
            'data': data or {}
        }

    def save(self):
        os.makedirs('data/{}'.format(self.info['id']))
        with open('data/{}/info.json'.format(self.info['id']), 'w') as f:
            f.write(json.dumps(self.info))
        for idx, face in enumerate(self.faces):
            cv2.imwrite('data/{}/img_CV2_{}.jpg'.format(self.info['id'], idx), face,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 90])


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
            root = os.path.join('data', str(id))
            for face in os.listdir(root):
                if face.endswith('.jpg'):
                    p.faces.append(cv2.imread(os.path.join(root, face)))

    @classmethod
    def get_data(cls):
        faces = []
        labels = []
        for p in cls.persons:
            for image in p.faces:
                try:
                    face, rect = detect_face(image)
                except NoFaces:
                    pass
                else:
                    faces.append(face)
                    labels.append(int(p.info['id']))
        return faces, labels

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
        person = _Person(id)
        if cls.persons:
            cls.persons.append(person)
        cv2.namedWindow("person")
        vc = cv2.VideoCapture(0)

        rval = vc.isOpened()

        im_cnt = 0
        save_faces = False
        while rval and im_cnt < 30:
            rval, frame = vc.read()
            if save_faces:
                cv2.imshow("person", frame)
                person.faces.append(frame)
                im_cnt += 1
                cv2.waitKey(80)
            else:
                util.draw_text(frame, 'Press \'y\' to start', 240, 40)
                cv2.imshow("person", frame)
                if cv2.waitKey(1) & 0xFF == ord('y'):
                    print('Pressed y, starting to save')
                    save_faces = True
        print('Faces: {}'.format(len(person.faces)))
        person.save()
        cv2.destroyWindow("person")
