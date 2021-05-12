## Detects blurry frames or fotos.
## Run on console with arguments i.e.: python3 MotionBlur_Detect.py --frames 'C:\..\.'

# import the necessary packages
from imutils import paths
import argparse
import cv2
import os, shutil
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)


quantity_analized = 0
quantity_blurry = 0
folder_for_rejected_blurry ="blurred_frames"

# print(type(paths.image_types))
# paths.image_types = paths.image_types + (".ARW", ".exr") #TO-DO: add other file types.
# logging.debug(paths.image_types)
# breakpoint()

def ARW_find(imageFile):
	# find the .ARW file alongside of .JPG foto.
	if os.path.isfile(imageFile) and str(os.path.splitext(imageFile)[1]).lower() == ".jpg":
		ARWfile = os.path.splitext(imageFile)[0] + ".ARW"
		if os.path.exists(ARWfile):
			logging.info(f"\nfund {ARWfile} companion of {imageFile} in this folder")
			return ARWfile

def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--frames", required=True,
	help="path to input directory of images")
ap.add_argument("-t", "--threshold", type=float, default=130.0,
	help="focus measures that fall below this max value will be considered 'blurry'")
ap.add_argument("-s", "--show", default=False,
	help="show the process")
args = vars(ap.parse_args())

working_folder = os.path.dirname(args["frames"])
logging.debug(f"working folder is: {working_folder}")

# loop over the input images
for n in np.arange(0.6, 1.01, 0.2)[::-1]:
	# threshold bracketing generator.
	args['threshold'] = round(args['threshold'] * round(n, 1), 1)
	logging.debug(f"         :: factor de threshold es f={args['threshold'] }")

	for imagePath in paths.list_images(args["frames"]):
		if os.path.isfile(imagePath):
			quantity_analized+=1
			# load the image, convert it to grayscale, and compute the
			# focus measure of the image using the Variance of Laplacian
			# method
			image = cv2.imread(imagePath , cv2.IMREAD_UNCHANGED )
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			fm = variance_of_laplacian(gray)
			text = "Not Blurry"
			# if the focus measure is less than the supplied threshold,
			# then the image should be considered "blurry"
			if fm < args["threshold"]:
				text = "Blurry"
				quantity_blurry +=1
				# move blurry frames to a separate sub-folder.
				file_name = imagePath.split(os.path.sep)[-1]
				blurred_frames_folder = os.path.join(working_folder,  f'{folder_for_rejected_blurry}_t{int(args["threshold"])}')
				if not os.path.exists(blurred_frames_folder):
					os.makedirs(blurred_frames_folder)
					logging.info(f"------------ folder created folder {blurred_frames_folder} ----------- \n")
				check_ARW = ARW_find(imagePath)
				if check_ARW:
					# move .jpg and .ARW file together.
					[shutil.move(i, blurred_frames_folder) for i in [check_ARW, imagePath]]
					# shutil.move(check_ARW, blurred_frames_folder)
					# shutil.move(imagePath, blurred_frames_folder)
					pass
				else:
					shutil.move(imagePath, blurred_frames_folder)


				# show the image
				if args["show"]:
					cv2.putText(image, "{}: {:.2f}".format(text, fm), (10, 30),
								cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
					cv2.imshow("Image", image)
					key = cv2.waitKey(0)

# finally will delete all empty folders to let the house in order.
for root, folder, filename in os.walk(working_folder, topdown=False):
	if len(os.listdir(root)) ==0 and os.path.isdir(root):
		logging.debug(f"\t the empty folder {root} will be deleted. ")
		shutil.rmtree(root)

logging.info(f"\n Found {quantity_blurry} blurry of {quantity_analized} analyzed frames in this folder.")