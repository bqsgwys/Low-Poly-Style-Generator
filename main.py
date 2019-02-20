#encoding=utf-8
import numpy as np
import cv2
from lowpoly import lowpoly, getstep
import tkinter as tk
from tkinter import filedialog
import cvui
from threading import Thread

WINDOW_NAME = 'App By BQSGWYS'
file_path = ""
cvui.init(WINDOW_NAME)
tk.Tk().withdraw()
frame = np.zeros((800, 300, 3), np.uint8)

kernalSize = [3]
gradientTV = [30.]
anchorTV = [8.]
scanIntervals = [1]
length = [3.]
times = [5.]
mean = [True]
alpha = [0.7]
ksize = [1]
exitFlag = False
imagefinal = 0
edgemap = 0
imgx = 0


def loader(image):
  global imgfinal
  global edgemap
  global imgx
  global exitFlag
  (imgfinal, edgemap, imgx) = lowpoly(
      image,
      kernalSize=(kernalSize[0], kernalSize[0]),
      length=length[0],
      gradientTV=gradientTV[0],
      anchorTV=anchorTV[0],
      scanIntervals=scanIntervals[0],
      Mean=mean[0],
      times=times[0],
      alpha=alpha[0],
      ksize=ksize[0])
  exitFlag = True


while True:
  # your app logic here
  frame[:] = (49, 52, 49)
  cvui.text(frame, 50, 750, 'Produced by BQSG', .6)
  cvui.beginColumn(frame, 10, 20)
  if (cvui.button("OpenFile")):
    file_path = filedialog.askopenfilename()
    print(file_path)
    try:
      image = cv2.imdecode(
          np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
      if image.shape[0] > image.shape[1]:
        image = cv2.resize(
            image, (int(800 * image.shape[1] / image.shape[0]), 800),
            interpolation=cv2.INTER_CUBIC)
      else:
        image = cv2.resize(
            image, (800, int(800 * image.shape[0] / image.shape[1])),
            interpolation=cv2.INTER_CUBIC)
    except:
      file_path = "cannot open the image"
      image = None
  cvui.space(10)
  cvui.text(file_path, 0.4)
  cvui.space(10)
  cvui.text("Kernal Size Gauss", 0.4)
  cvui.space(5)
  cvui.trackbar(250, kernalSize, 1, 11, 5, '%d', cvui.TRACKBAR_DISCRETE, 2)
  cvui.space(10)
  cvui.text("Kernal Size Sobel", 0.4)
  cvui.space(5)
  cvui.trackbar(250, ksize, 1, 11, 5, '%d', cvui.TRACKBAR_DISCRETE, 2)
  cvui.space(10)
  cvui.text("Grey or Bright", 0.4)
  cvui.space(5)
  cvui.trackbar(250, alpha, 0, 1)
  cvui.space(10)
  cvui.text("Gradient Therehold Value", 0.4)
  cvui.space(5)
  cvui.trackbar(250, gradientTV, 0, 50, 5)
  cvui.space(10)
  cvui.text("Anchor Therehold Value", 0.4)
  cvui.space(5)
  cvui.trackbar(250, anchorTV, 0, 20, 5)
  cvui.space(10)
  cvui.text("Minimum Distance", 0.4)
  cvui.space(5)
  cvui.trackbar(250, length, 0, 20, 5)
  cvui.space(10)
  cvui.text("Sparse Area Coefficient", 0.4)
  cvui.space(5)
  cvui.trackbar(250, times, 1, 10, 5)
  cvui.space(10)
  cvui.text("Scan interval", 0.4)
  cvui.space(5)
  cvui.trackbar(250, scanIntervals, 1, 5, 4, '%d', cvui.TRACKBAR_DISCRETE, 1)
  cvui.space(10)
  cvui.checkbox('Mean or Mid', mean)
  cvui.space(10)

  if (cvui.button("Process")):
    THD = Thread(target=loader, args=(image,))
    THD.start()

  cvui.space(10)
  cvui.text(str(getstep() * 20) + '%', 0.8)
  cvui.space(10)

  cvui.endColumn()
  # Show window content
  if exitFlag:
    exitflag = False
    cv2.imshow("origin", image)
    cv2.imshow("final", imgfinal)
    cv2.imshow("edges", edgemap)
    cv2.imshow("anchors", imgx)
  cvui.imshow(WINDOW_NAME, frame)
  if cv2.waitKey(20) == 27:
    break
'''
file_path = filedialog.askopenfilename()
cap = cv2.VideoCapture()
setconfig(grad=15, anch=7)
while 1:
  ret, img = cap.read()
  low, maps = lowpoly(img)
  cv2.imshow('img', img)
  cv2.imshow('lowpoly', low)
  cv2.imshow('edgemap', maps)
  # print(bases)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break
cv2.destroyAllWindows()'''