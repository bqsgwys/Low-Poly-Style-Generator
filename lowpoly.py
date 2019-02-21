import numpy as np
import cv2
from numba import jit, cuda
from math import *
import random

HORIZONTAL = 1
VERTICAL = -1
STEP = 0
global rect

#configurations and therehold values


@jit(parallel=True)
def color(img, pt):
  return img[int(pt[1])][int(pt[0])]


def getstep():
  global STEP
  return STEP


def addstep():
  global STEP
  STEP = (STEP + 1) % 5
  # print(STEP)


@jit(parallel=True)
def avg(a, b, c):
  return (round((a[0] + b[0] + c[0]) / 3), round((a[1] + b[1] + c[1]) / 3))


@jit(parallel=True)
def dis(a, b):
  return sqrt((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]))


@jit(parallel=True)
def time(k, b):
  return (k * b[0], k * b[1])


@jit(parallel=True)
def plus(a, b):
  return (a[0] + b[0], a[1] + b[1])


@jit(parallel=True)
def minus(a, b):
  return (a[0] - b[0], a[1] - b[1])


@jit(parallel=True)
def rd(a):
  return (round(a[0]), round(a[1]))


@jit(parallel=True)
def getAnchor(
    img,
    smoothed=False,
    gradientTV=30.,
    anchorTV=8.,
    scanIntervals=1,
    ksize=1,
):
  #check the img
  if len(img.shape) > 2:
    raise ('Use only 1 channel or grayscale image')
    return None
  # compute dx,dy imagegradient
  dxImg = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=ksize)
  dyImg = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=ksize)
  # Compute gradient map and direction map
  gradient = np.sqrt(dxImg * dxImg + dyImg * dyImg)
  gradient[gradient < gradientTV] = 0  # Denoising
  direction = -np.sign(np.abs(dxImg) - np.abs(dyImg))
  direction[gradient < gradientTV] = 0  # Denoising
  anchorlist = []
  for i in range(1, img.shape[0] - 1, scanIntervals):
    for j in range(1, img.shape[1] - 1, scanIntervals):
      if direction[i, j] == HORIZONTAL:
        # HORIZONTAL EDGE compare up & down
        if gradient[i, j] - gradient[i - 1, j] >= anchorTV \
              and gradient[i, j] - gradient[i + 1, j] >= anchorTV:
          anchorlist.append((i, j))
      elif direction[i, j] == VERTICAL:
        # VERTICAL EDGE. Compare with left & right.
        if gradient[i, j] - gradient[i, j - 1] >= anchorTV \
              and gradient[i, j] - gradient[i, j + 1] >= anchorTV:
          anchorlist.append((i, j))
  return anchorlist


@jit(parallel=True)
def rectcontains(rect, point):
  if point[0] <= rect[0]:
    return False
  elif point[1] <= rect[1]:
    return False
  elif point[0] >= rect[2]:
    return False
  elif point[1] >= rect[3]:
    return False
  return True


@jit(parallel=True)
def lowpoly(img,
            kernalSize=(3, 3),
            gradientTV=30.,
            anchorTV=8.,
            scanIntervals=1,
            length=3.,
            times=5.,
            Mean=True,
            alpha=0.7,
            ksize=1):
  # smooth the picture
  imgx = cv2.GaussianBlur(img, kernalSize, 0)
  # get the GREY tunnel and the VALUE in HSV space
  h, s, v = cv2.split(cv2.cvtColor(imgx, cv2.COLOR_BGR2HSV))
  grey = cv2.cvtColor(imgx, cv2.COLOR_BGR2GRAY)
  v = cv2.addWeighted(v, alpha, grey, 1 - alpha, 0)
  w = img.shape[0]
  h = img.shape[1]
  rect = (0, 0, h, w)
  bases = [(1, 1), (1, w - 1), (h - 1, 1), (h - 1, w - 1)]
  # get anchors
  anchor = getAnchor(v, False, gradientTV, anchorTV, scanIntervals, ksize)

  addstep()
  # randomized insert anchors(min distance)
  random.shuffle(anchor)
  for i in range(len(anchor)):
    flag = True
    anchor[i] = (anchor[i][1], anchor[i][0])
    if rectcontains(rect, anchor[i]):
      for pts in bases:
        if dis(anchor[i], pts) <= length:
          flag = False
          break
      if flag:
        bases.append(anchor[i])

  addstep()
  # insert random points(min distance)
  cnt = 80
  while cnt > 0:
    flag = True
    (x, y) = (np.random.randint(h), np.random.randint(w))
    while not rectcontains(rect, (x, y)):
      (x, y) = (np.random.randint(h), np.random.randint(w))
    for pts in bases:
      if dis((x, y), pts) < times * length:
        cnt -= 1
        flag = False
        break
    if flag:
      cnt = 80
      if rectcontains(rect, (x, y)):
        bases.append((x, y))

  addstep()
  # calculate Delaunay Triangulation
  subdiv = cv2.Subdiv2D()
  subdiv.initDelaunay(rect)
  subdiv.insert(bases)

  # draw tringles
  addstep()
  triangleList = subdiv.getTriangleList()
  imgfinal = np.zeros(img.shape, np.uint8)
  edgemap = np.zeros(img.shape[:2], np.uint8)
  for t in triangleList:
    pt1 = (t[0], t[1])
    pt2 = (t[2], t[3])
    pt3 = (t[4], t[5])
    if rectcontains(rect, pt1) and rectcontains(rect, pt2) and rectcontains(
        rect, pt3):
      ptt = np.array([[pt1, pt2, pt3]]).astype(np.int32)
      if Mean:
        mask = np.zeros(img.shape[:2], np.uint8)
        cv2.drawContours(mask, ptt, 0, 255, -1)
        mean = cv2.mean(img, mask)
      else:
        ag = avg(pt1, pt2, pt3)
        c1 = color(img, pt1)
        c2 = color(img, pt2)
        c3 = color(img, pt3)
        c4 = color(img, ag)
        td1 = round((int(c1[0]) + int(c2[0]) + int(c3[0]) + int(c4[0])) / 4)
        td2 = round((int(c1[1]) + int(c2[1]) + int(c3[1]) + int(c4[1])) / 4)
        td3 = round((int(c1[2]) + int(c2[1]) + int(c3[2]) + int(c4[2])) / 4)
        mean = (td1, td2, td3)
      cv2.drawContours(imgfinal, ptt, 0, mean, -1)
      cv2.line(edgemap, pt1, pt2, 255, 1)
      cv2.line(edgemap, pt2, pt3, 255, 1)
      cv2.line(edgemap, pt3, pt1, 255, 1)
      cv2.circle(imgx, pt1, 2, (255, 255, 255), 1)
      cv2.circle(imgx, pt2, 2, (255, 255, 255), 1)
      cv2.circle(imgx, pt3, 2, (255, 255, 255), 1)
  addstep()
  return (imgfinal, edgemap, imgx)


@jit
def simplepoly(img,
               kernalSize=(3, 3),
               gradientTV=30.,
               anchorTV=8.,
               scanIntervals=1,
               length=3.,
               times=5.,
               Mean=True,
               alpha=0.7,
               ksize=1):
  # smooth the picture
  imgx = cv2.GaussianBlur(img, kernalSize, 0)
  # get the GREY tunnel and the VALUE in HSV space
  h, s, v = cv2.split(cv2.cvtColor(imgx, cv2.COLOR_BGR2HSV))
  grey = cv2.cvtColor(imgx, cv2.COLOR_BGR2GRAY)
  v = cv2.addWeighted(v, alpha, grey, 1 - alpha, 0)
  w = img.shape[0]
  h = img.shape[1]
  rect = (0, 0, h, w)
  bases = [(1, 1), (1, w - 1), (h - 1, 1), (h - 1, w - 1)]
  # get anchors
  anchor = getAnchor(v, False, gradientTV, anchorTV, scanIntervals, ksize)

  # randomized insert anchors(min distance)
  random.shuffle(anchor)
  for i in range(len(anchor)):
    flag = True
    anchor[i] = (anchor[i][1], anchor[i][0])
    if rectcontains(rect, anchor[i]):
      for pts in bases:
        if dis(anchor[i], pts) <= length:
          flag = False
          break
      if flag:
        bases.append(anchor[i])

  # insert random points(min distance)
  cnt = 80
  while cnt > 0:
    flag = True
    (x, y) = (np.random.randint(h), np.random.randint(w))
    while not rectcontains(rect, (x, y)):
      (x, y) = (np.random.randint(h), np.random.randint(w))
    for pts in bases:
      if dis((x, y), pts) < times * length:
        cnt -= 1
        flag = False
        break
    if flag:
      cnt = 80
      if rectcontains(rect, (x, y)):
        bases.append((x, y))

  # calculate Delaunay Triangulation
  subdiv = cv2.Subdiv2D()
  subdiv.initDelaunay(rect)
  subdiv.insert(bases)

  # draw tringles
  triangleList = subdiv.getTriangleList()
  imgfinal = np.zeros(img.shape, np.uint8)
  for t in triangleList:
    pt1 = (t[0], t[1])
    pt2 = (t[2], t[3])
    pt3 = (t[4], t[5])
    if rectcontains(rect, pt1) and \
       rectcontains(rect, pt2) and \
       rectcontains(rect, pt3):
      ptt = np.array([[pt1, pt2, pt3]]).astype(np.int32)
      if Mean:
        mask = np.zeros(img.shape[:2], np.uint8)
        cv2.drawContours(mask, ptt, 0, 255, -1)
        mean = cv2.mean(img, mask)
      else:
        ag = avg(pt1, pt2, pt3)
        c1 = color(img, pt1)
        c2 = color(img, pt2)
        c3 = color(img, pt3)
        c4 = color(img, ag)
        td1 = round((int(c1[0]) + int(c2[0]) + int(c3[0]) + int(c4[0])) / 4)
        td2 = round((int(c1[1]) + int(c2[1]) + int(c3[1]) + int(c4[1])) / 4)
        td3 = round((int(c1[2]) + int(c2[1]) + int(c3[2]) + int(c4[2])) / 4)
        mean = (td1, td2, td3)
      cv2.drawContours(imgfinal, ptt, 0, mean, -1)
  return imgfinal