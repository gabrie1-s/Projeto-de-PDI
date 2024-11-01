import cv2
from copy import deepcopy
    

def process(img):
    output = deepcopy(img)
    jeans = cv2.blur(output, (13,13))
    _, jeans = cv2.threshold(jeans, 20, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(jeans, 50, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    coordinates = []
    for idx, contour in enumerate(contours):
        length = cv2.arcLength(contour, closed=True)
        if length < 260: continue

        x,y,w,h = cv2.boundingRect(contour)
        coordinates.append([x,y,w,h])
        
    return {
        'fails': coordinates,
    }
