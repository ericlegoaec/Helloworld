import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

# image = cv2.imread("sample2.png")
# gaussian_3 = cv2.GaussianBlur(image, (9,9), 10.0)
# unsharp_image = cv2.addWeighted(image, 1.5, gaussian_3, -0.5, 0, image)
# cv2.imwrite("sample2_unsharp.png", unsharp_image)


img = cv2.imread('sample2.png',0)
ret,th1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
th2 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
titles = ['Original Image', 'Global Thresholding (v = 127)',
            'Adaptive Mean Thresholding', 'Adaptive Gaussian Thresholding']
images = [img, th1, th2, th3]
for i in range(4):
    plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])
plt.show()

cv2.imwrite("sample2_after.png", th3)