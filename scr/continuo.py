import numpy as np
import basler_camera as cam
import watchdog 
import matplotlib.pyplot as plt
import cv2
import seriais
import threading
import time
import queue



serial1, serial2, serial3, bancada = seriais.NumerosSeriais()
camera = cam.Camera(bancada,exposicao=60000, ganho = 10, fps=200)
camera.conectar()


thread1 = threading.Thread(target = camera.filme)
thread1.start()


cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
cv2.resizeWindow('1', 1216, 1936)

data = []
while True:
    try:
   
        img = camera.array
        #img= cv2.applyColorMap(camera.array, cv2.COLORMAP_PLASMA)
        
        #print(np.mean(img))
        data.append(round(np.mean(img),2))
        print(camera.fps_aquisitado,camera.fps_transferido)
        cv2.imshow('Frame',img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.movie=False
            break
        
        
    except Exception as e:
        camera.movie=False
        print(e)
        print(camera.array,camera.array.shape)
        print('Medida falhou')

cv2.destroyAllWindows()

plt.plot([x for x in range(len(data))],data)
plt.show()