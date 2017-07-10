import cv2
from PIL import Image

# image = cv2.imread("sample2.png")
# gaussian_3 = cv2.GaussianBlur(image, (9,9), 10.0)
# unsharp_image = cv2.addWeighted(image, 1.5, gaussian_3, -0.5, 0, image)
# cv2.imwrite("sample2_unsharp.png", unsharp_image)


def remove_noise(im):
	im_width, im_height = im.size
	denoised_im = Image.new("L", (im_width, im_height))

	for i in range(0, im_width):
		for j in range(0, im_height):
			x = im.getpixel((i, j))
			if (x < 162):
				denoised_im.paste(0, (im_width-i, im_height-j))
			else:
				denoised_im.paste(255, (im_width-i, im_height-j))

	return denoised_im


im = Image.open("sample2.png")
bw_im  = im.convert('L')
denoised_im = remove_noise(bw_im)
denoised_im.save("sample2_after.png")