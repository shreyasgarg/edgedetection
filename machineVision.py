from tkinter import *
from time import clock
from sys import setrecursionlimit
setrecursionlimit(7000)

root = Tk()
START = clock()
WIDTH = 512
HEIGHT = 512
COLORFLAG = False
HIGH = 45
LOW = 10
NUMBER_OF_TIMES_TO_SMOOTH_IMAGE = 7

class ImageFrame:
  def __init__(self,pixels):
    self.img = PhotoImage(width = WIDTH, height = HEIGHT)
    for row in range(HEIGHT):
      for col in range(WIDTH):
        num = pixels[row*WIDTH + col]
        if COLORFLAG == TRUE:
          kolor = '#%02x%02x%02x' % (num[0],num[1],num[2])
        else:
          kolor = '#%02x%02x%02x' % (num,num,num)
        self.img.put(kolor,(col,row))
    c = Canvas(root,width = WIDTH, height = HEIGHT); c.pack()
    c.create_image(0,0,image = self.img, anchor = NW)
    printElapsedTime('displayed image')

def printElapsedTime(msg = 'time'):
  length = 30
  msg = msg[:length]
  tab = '.'*(length - len(msg))
  print('--' + msg.upper() + tab + ' ', end = '')
  time = round(clock() - START,1)
  print('%2d'%int(time/60), ' min "', '%4.1f'%round(time%60,1), ' sec', sep = '')

def readFileNumbersIntoString(file1):
  nums = file1.read().split()
  nums = nums[4:]
  file1.close
  if len(nums) % 3 != 0:
    print("WRONG FILE SIZE")
    exit()
  return nums

def convertStringRGSstoGrayIntegerOrColorTuples(nums):
  IMAGE = []
  if COLORFLAG == True:
    for pos in range(0,len(nums),3):
      IMAGE.append((int(nums[pos]),int(nums[pos+1]),int(nums[pos+2])))
  else:
    for pos in range(0,len(nums),3):
      IMAGE.append(int(nums[pos])*.3 + .59*int(nums[pos+1]) + .11*int(nums[pos+2]))
  return IMAGE

def smooth(image,NUMBER_OF_TIMES_TO_SMOOTH_IMAGE):
  for num in range(NUMBER_OF_TIMES_TO_SMOOTH_IMAGE):
    for row in range(1,HEIGHT-1):
      for col in range(1,WIDTH-1):
        image[row*WIDTH + col] = function(row,col,image)
  return image
      
def function(row,col,image):
  add = image[row*WIDTH + col] * 4
  add+= image[(row-1) * WIDTH + col] * 2
  add+= image[(row-1) * WIDTH + col-1]
  add+= image[(row-1) * WIDTH + col+1]
  add+= image[row * WIDTH + col+1] * 2
  add+= image[row * WIDTH + col-1] * 2
  add+= image[(row+1) * WIDTH + col] * 2
  add+= image[(row+1) * WIDTH + col-1]
  add+= image[(row+1) * WIDTH + col+1]
  return add//16

def calcGrads(image,row,col):
  add = image[(row-1) * WIDTH + col-1] * -1
  add+= image[(row-1) * WIDTH + col+1]
  add+= image[row * WIDTH + col+1] * 2
  add+= image[row * WIDTH + col-1] * -2
  add+= image[(row+1) * WIDTH + col-1] * -1
  add+= image[(row+1) * WIDTH + col+1]
  
  oth = image[(row-1) * WIDTH + col] * 2
  oth+= image[(row-1) * WIDTH + col-1]
  oth+= image[(row-1) * WIDTH + col+1]
  oth+= image[(row+1) * WIDTH + col] * -2
  oth+= image[(row+1) * WIDTH + col-1] * -1
  oth+= image[(row+1) * WIDTH + col+1] * -1
  
  return add,oth

def theta(x,y):
  from math import atan2,degrees
  x = round(degrees(atan2(y,x)),2)
  if x < 0:
    x += 180
  if x <= 22.5:
    return 0
  if x <= 67.5:
    return 1
  if x <= 112.5:
    return 2
  if x <= 157.5:
    return 3
  else:
    return 0

def sobelTransformation(image):
  image2 = [0 for elt in range(HEIGHT*WIDTH)]
  for row in range(HEIGHT):
      for col in range(WIDTH):
        if row == 0 or col == 0 or row == HEIGHT -1 or col == WIDTH - 1:
          image2[row*WIDTH + col] = (0,0,0,0,0)
        else:
          Gx,Gy = calcGrads(image,row,col)
          t = theta(Gx,Gy)
          from math import sqrt
          image2[row*WIDTH + col] = (sqrt(Gx*Gx + Gy*Gy),t,0,0,0)
  return image2

def normalize(thing):
  big = max(thing)
  for x in range(len(thing)):
    thing[x] = int(thing[x] * 255/big)
  return thing

def cannyTransform(image):
  image2 = []
  for row in range(HEIGHT):
    for col in range(WIDTH):
      tup = image[row*WIDTH + col]
      tupl = [tup[0],tup[1],0,0,0]
      if row != 0 and col != 0 and row != HEIGHT - 1 and col != WIDTH - 1 and tupl != [0,0,0,0,0]:
        direct = tupl[1]
        if direct == 0:
          if tupl[0] > image[row*WIDTH + col + 1][0] and tupl[0] > image[row*WIDTH + col - 1][0]:
            tupl[2] = 1
        elif direct == 1:
          if tupl[0] > image[(row+1)*WIDTH + col + 1][0] and tupl[0] > image[(row-1)*WIDTH + col - 1][0]:
            tupl[2] = 1
        elif direct == 2:
          if tupl[0] > image[(row-1)*WIDTH + col][0] and tupl[0] > image[(row+1)*WIDTH + col][0]:
            tupl[2] = 1
        elif direct == 3:
          if tupl[0] > image[(row+1)*WIDTH + col - 1][0] and tupl[0] > image[(row-1)*WIDTH + col + 1][0]:
            tupl[2] = 1
      image2.append(tupl)
  return image2

def doubleThreshold(image):
  coords = []
  for row in range(HEIGHT):
    for col in range(WIDTH):
      if image[row*WIDTH + col][2] == 1 and image[row*WIDTH + col][0] > HIGH:
        image[row * WIDTH + col][4] = 1
        coords.append((row,col))
  for thing in coords:
    fixCellAt(thing[0],thing[1],image)
  return image
  
def fixCellAt(row,col,m):
  if m[row*WIDTH + col][3] == 1: return
  m[row * WIDTH + col][3] = 1
  
  if row > 0 and m[(row-1)*WIDTH + col][2] == 1 and m[(row-1)*WIDTH + col][0] > LOW:
    m[(row-1)*WIDTH + col][3] = 1
    m[(row-1)*WIDTH + col][4] = 1
    fixCellAt(row-1,col,m)
    
  if row < 512 and m[(row+1)*WIDTH + col][2] == 1 and m[(row+1)*WIDTH + col][0] > LOW:
    m[(row+1)*WIDTH + col][3] = 1
    m[(row+1)*WIDTH + col][4] = 1
    fixCellAt(row+1,col,m)
    
  if col > 0 and m[(row)*WIDTH + col-1][2] == 1 and m[(row)*WIDTH + col-1][0] > LOW:
    m[(row)*WIDTH + col-1][3] = 1
    m[(row)*WIDTH + col-1][4] = 1
    fixCellAt(row,col-1,m)
    
  if col < 512 and m[(row)*WIDTH + col+1][2] == 1 and m[(row)*WIDTH + col+1][0] > LOW:
    m[(row)*WIDTH + col+1][3] = 1
    m[(row)*WIDTH + col+1][4] = 1
    fixCellAt(row,col+1,m)
    
def printTitleAndSizeOfImageInPixels(image):
  print('           ==<RUN TIME INFORMATION>==')
  if len(image) != WIDTH * HEIGHT:
    print('--ERROR: Stated file size not equal to number of pixels')
    print('file length:', len(image))
    print('width:', WIDTH, 'height:', HEIGHT)
    exit()
  print("--NUMBER OF PIXELS...........", len(image))
  printElapsedTime('image extracted from file')
  
def readPixelColorsFromFile(file1):
  nums = readFileNumbersIntoString(file1)
  image = convertStringRGSstoGrayIntegerOrColorTuples(nums)
  printTitleAndSizeOfImageInPixels(image)
  return image
  
def main():
  fileName1 = 'lena_rgb_p3.ppm'
  file1 = open(fileName1,'r')
  
  image = readPixelColorsFromFile(file1)
  #x = ImageFrame(image)
  
  image = smooth(image,NUMBER_OF_TIMES_TO_SMOOTH_IMAGE)
  #x = ImageFrame(image)
  image = sobelTransformation(image)
  sobelMagnitudes = []
  for thing in image:
    sobelMagnitudes.append(thing[0])
  image2 = normalize(sobelMagnitudes)
  #x = ImageFrame(image2)
  
  image = cannyTransform(image)
  image = doubleThreshold(image)
  image3 = []
  for thing in image:
    if thing[4] == 1:
      image3.append(255)
    else:
      image3.append(0)
  x = ImageFrame(image3)
  root.mainloop()
  
if __name__ == '__main__': main()