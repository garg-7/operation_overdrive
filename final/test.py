import cv2
import numpy as np
import pyautogui
import time

def screenShareSave(scr_m):
    # display screen resolution, get it from your OS settings
    SCREEN_SIZE = (1366, 768)
    # define the codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # create the video write object
    out = cv2.VideoWriter("server_screen.avi", fourcc, 18.0, (SCREEN_SIZE))
    # count=0
    # start_time = time.time()
    while scr_m.keep_going:
        # make a screenshot
        img = pyautogui.screenshot()
        # img = pyautogui.screenshot(region=(0, 0, 300, 400))
        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(img)
        # convert colors from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # write the frame
        out.write(frame)
        # count+=1
        # show the frame
        #cv2.imshow("screenshot", frame)
        # if the user clicks q, it exits
        if cv2.waitKey(1) == ord("q"):
            break
    
    # print(f"{count/20}")
    # make sure everything is closed when exited
    # cv2.destroyAllWindows()
    out.release()

if __name__=='__main__':
    screenShareSave()