#encoding=utf-8
import numpy as np
import cv2
from lowpoly import lowpoly, getstep, simplepoly
import tkinter as tk
from tkinter import filedialog
import cvui
from threading import Thread

WINDOW_NAME = 'App By BQSGWYS'
file_path = ""
cvui.init(WINDOW_NAME)
tk.Tk().withdraw()
frame = np.zeros((800, 300, 3), np.uint8)

global sumcnt
kernalSize = [3]
gradientTV = [30.]
anchorTV = [8.]
scanIntervals = [1]
length = [3.]
times = [5.]
mean = [True]
isVideo = [False]
alpha = [0.7]
ksize = [1]
exitFlag = False
imagefinal = 0
edgemap = 0
imgx = 0

outcnt = 0
sumcnt = 1
readcnt = 0
frams = []
toframs = []
tpool = []


def getperc():
  if isVideo[0]:
    return str(round(outcnt / sumcnt * 100))
  else:
    return str(getstep() * 20)


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


def videos(modi, orii):
  global outcnt
  global frams
  global toframs
  for i in range(len(toframs)):
    if i % modi == orii:
      toframs[i] = simplepoly(
          frams[i],
          kernalSize=(kernalSize[0], kernalSize[0]),
          length=length[0],
          gradientTV=gradientTV[0],
          anchorTV=anchorTV[0],
          scanIntervals=scanIntervals[0],
          Mean=mean[0],
          times=times[0],
          alpha=alpha[0],
          ksize=ksize[0])
      outcnt += 1
      print(outcnt)


def saveimg(img, name):
  cv2.imencode(
      ".jpg",
      simplepoly(
          img,
          kernalSize=(kernalSize[0], kernalSize[0]),
          length=length[0],
          gradientTV=gradientTV[0],
          anchorTV=anchorTV[0],
          scanIntervals=scanIntervals[0],
          Mean=mean[0],
          times=times[0],
          alpha=alpha[0],
          ksize=ksize[0]))[1].tofile(name + "lowpoly.jpg")


startFlag = False
global thds
thds = 7
global Size
while True:
  # your app logic here
  frame[:] = (49, 52, 49)
  cvui.text(frame, 50, 750, 'Produced by BQSG', .6)
  cvui.beginColumn(frame, 10, 20)
  if (cvui.button("OpenFile")):
    file_path = filedialog.askopenfilename()
    # print(file_path)
    if isVideo[0]:
      try:
        cap = cv2.VideoCapture(file_path)
        sumcnt = int(round(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        print(sumcnt)
        for i in range(sumcnt):
          ret, image = cap.read()
          if ret:
            if image.shape[0] > image.shape[1]:
              image = cv2.resize(
                  image, (int(800 * image.shape[1] / image.shape[0]), 800),
                  interpolation=cv2.INTER_CUBIC)
            else:
              image = cv2.resize(
                  image, (800, int(800 * image.shape[0] / image.shape[1])),
                  interpolation=cv2.INTER_CUBIC)
            Size = image.shape
            frams.append(image)
            toframs.append(0)
          else:
            sumcnt -= 1
      except:
        file_path = "cannot open the video"
        cap = None

      for i in range(thds):
        tpool.append(Thread(target=videos, args=(thds, i)))
    else:
      try:
        image = cv2.imdecode(
            np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image.shape[0] > image.shape[1]:
          imag = cv2.resize(
              image, (int(800 * image.shape[1] / image.shape[0]), 800),
              interpolation=cv2.INTER_CUBIC)
        else:
          imag = cv2.resize(
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
  cvui.space(5)
  cvui.beginRow()
  cvui.checkbox('Mean or Mid', mean)
  cvui.space(5)
  cvui.checkbox('Video', isVideo)
  cvui.endRow()
  cvui.space(5)
  cvui.beginRow()
  if (cvui.button("Process")):
    if isVideo[0]:
      outcnt = 0
      for i in range(thds):
        tpool[i].start()
      startFlag = True
    else:
      THD = Thread(target=loader, args=(imag,))
      THD.start()
  cvui.space(5)
  if cvui.button('&Quit'):
    break
  if not isVideo[0]:
    cvui.space(5)
    if cvui.button('&Save'):
      Thread(target=saveimg, args=(image, file_path)).start()
  cvui.endRow()
  cvui.space(10)
  cvui.text(getperc() + '%', 0.8)
  cvui.space(10)

  cvui.endColumn()
  # Show window content
  if startFlag and outcnt == sumcnt:
    fps = cap.get(cv2.CAP_PROP_FPS)
    vw = None
    print((Size[0], Size[1]))
    vw = cv2.VideoWriter("out.avi", cv2.VideoWriter_fourcc(*'XVID'), fps,
                         (Size[1], Size[0]), True)
    print(vw.isOpened())
    for i in range(sumcnt):
      # cv2.imshow("origin", toframs[i])
      vw.write(toframs[i])
    vw.release()
    startFlag = False
    print("ok")
  if exitFlag:
    exitflag = False
    cv2.imshow("origin", imag)
    cv2.imshow("final", imgfinal)
    cv2.imshow("edges", edgemap)
    cv2.imshow("anchors", imgx)
  cvui.imshow(WINDOW_NAME, frame)
  if cv2.waitKey(20) == 27:
    break
