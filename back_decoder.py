import os

import numpy as np
from PIL import Image
from sklearn import svm
from sklearn import cross_validation
from sklearn.externals import joblib

from utils import *


class BackRecognizer:
    def __init__(self):
        self.trainingData = []
        self.targetValues = []
        self.svc = svm.SVC(gamma=0.001, kernel="linear", C=100)
        self.down_res = (100, 100)

    def _load(self, path, target_value):
        training_imgs = os.listdir(path)
        for f in training_imgs:
            if f.endswith('.db'):
                continue
            img = Image.open(path + '/' + f)
            img = img.resize(self.down_res, Image.BILINEAR)
            self.trainingData.append(np.array(img.getdata()).flatten())
            self.targetValues.append(target_value)

    def load(self):
        pt = 'Training_Data/Back'
        self._load(pt + '/curtain', curtain)
        self._load(pt + '/end', end)
        self._load(pt + '/intro', intro)
        self._load(pt + '/loading', loading)
        self._load(pt + '/scoreboard', scoreboard)
        self._load(pt + '/shop', shop)

    def train(self):
        folder = 'back_dat'
        pt = os.getcwd() + '/' + folder
        if os.path.isdir(folder):
            dat = os.listdir(pt)
            if not int(len(dat)) == 0:
                self.svc = joblib.load(pt + '/' + back_recognizer)
            else:
                self.learn_dat(pt)
        else:
            os.mkdir(pt)
            self.learn_dat(pt)

    def learn_dat(self, path):
        self.load()
        np_data = np.array(self.trainingData)
        np_values = np.array(self.targetValues)
        self.svc.fit(np_data, np_values)
        joblib.dump(self.svc, path + '/' + back_recognizer)

    def test(self):
        np_train_data = np.array(self.trainingData)
        np_values = np.array(self.targetValues)
        data, test_data, train_target, test_target = cross_validation.train_test_split(np_train_data, np_values,
                                                                                       test_size=0.4, random_state=0)
        self.svc.fit(data, train_target)
        pass

    def predict(self, img):
        resized_img = img.resize(self.down_res, Image.BILINEAR)
        np_img = np.array(resized_img.getdata()).flatten()
        return int(self.svc.predict(np_img))
