import cv2

# image_path
img_path = "C:\\Users\\cdgs\\Desktop\\file_uploading\\base_img\\cm2_base_img.jpg"


# read image
img_raw = cv2.imread(img_path)

if img_raw is None:
    print(f"Failed to load image at {img_path}")
    exit()

# Set a fixed desired size for display
desired_width = 800
desired_height = 600

# Calculate the scaling factors
scale_width = desired_width / img_raw.shape[1]
scale_height = desired_height / img_raw.shape[0]
scaling_factor = min(scale_width, scale_height)

# Resize the image for display
img_display = cv2.resize(img_raw, None, fx=scaling_factor, fy=scaling_factor)

try:
    while True:
        # Select ROI function on the resized image
        roi = cv2.selectROI(img_display)
        print(f"Selected ROI (on displayed/resized image): {roi}")

        # Convert the ROI coordinates back to the original image scale
        roi_original = (
            int(roi[0] / scaling_factor),
            int(roi[1] / scaling_factor),
            int(roi[2] / scaling_factor),
            int(roi[3] / scaling_factor)
        )
        
        print(f"Mapped ROI (on original image): {roi_original}")

        # Crop from the original image using scaled ROI
        roi_cropped_original = img_raw[
            roi_original[1] : roi_original[1] + roi_original[3], 
            roi_original[0] : roi_original[0] + roi_original[2]
        ]

        # Show cropped image from original
        cv2.imshow("ROI", roi_cropped_original)

        # Hold window until a key is pressed
        cv2.waitKey(0)
except KeyboardInterrupt:
    pass

# Destroy all OpenCV windows when done
cv2.destroyAllWindows()
