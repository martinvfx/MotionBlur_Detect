## Detects blurry frames or fotos.
## Run on console with arguments i.e.: python3 MotionBlur_Detect.py --frames C:\...

# import the necessary packages
from imutils import paths
import argparse
import cv2
import os, shutil
import logging
logging.basicConfig(level=logging.DEBUG)


quantity_analized = 0
quantity_blurry = 0
folder_for_rejected_blurry = "blurred_frames"

def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--frames", required=True,
	help="path to input directory of images")
ap.add_argument("-t", "--threshold", type=float, default=130.0,
	help="focus measures that fall below this value will be considered 'blurry'")
ap.add_argument("-s", "--show", default=False,
	help="show the process")
args = vars(ap.parse_args())



# loop over the input images
for imagePath in paths.list_images(args["frames"]):
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
		working_folder = os.path.dirname(imagePath)
		# logging.debug(f"folder is: {working_folder}")
		blurred_frames_folder = os.path.join(working_folder, folder_for_rejected_blurry)
		if not os.path.exists(blurred_frames_folder):
			os.makedirs(blurred_frames_folder)
		shutil.move(imagePath, blurred_frames_folder)

	# show the image
	if args["show"]:
		cv2.putText(image, "{}: {:.2f}".format(text, fm), (10, 30),
		cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
		cv2.imshow("Image", image)
		key = cv2.waitKey(0)

logging.info(f"\n Found {quantity_blurry} of {quantity_analized} analyzed frames in this folder.")