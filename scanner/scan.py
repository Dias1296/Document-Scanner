from transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse, cv2, imutils

#Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image to be scanned")
args = vars(ap.parse_args())

#Load the image and compute the ratio of the old height to the new height, clone it and resize it
print(args["image"])
image = cv2.imread(args["image"])
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height = 500)

#Convert the image to grayscale, blur it, and find edges in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)

#Show the original image and the edge detected image
print("STEP 1: Edge Detetection")
cv2.imshow("Image", image)
cv2.imshow("Edged", edged)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#Find the contours in the edged image, keeping only the largest ones, and initialize the screen contour
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True) [:5]

#Loop over the contours
for c in cnts:
  # Approximate the contour
  peri = cv2.arcLength(c, True)
  approx = cv2.approxPolyDP(c, 0.02 * peri, True)

  #If our approximated contour has four points, then we can assume that we 
  #have found our screen
  if len(approx) == 4:
    screenCnt = approx
    break

#Show the contour (outline) of the piece of paper
print("STEP 2: Find contours of paper")
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv2.imshow("Outline", image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#Apply the four point transform to obtain a top-down view of the original image
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

#Convert the warped image to grayscale, then threshold it to give it that 
#'black and white' paper effect
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
T = threshold_local(warped, 11, offset = 10, method="gaussian")
warped = (warped > T).astype("uint8") * 255

#Show the original and scanned images
print("Step 3: Apply perspective transform")
cv2.imshow("Original", imutils.resize(orig, height = 650))
cv2.imshow("Scanned", imutils.resize(warped, height = 650))
cv2.waitKey(0)