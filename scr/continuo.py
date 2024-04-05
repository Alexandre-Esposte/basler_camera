import numpy as np
import basler_camera as cam
import watchdog 
import matplotlib.pyplot as plt
import cv2
import seriais
import threading
import time
import queue
import os



serial1, serial2, serial3, bancada = seriais.NumerosSeriais()
camera = cam.Camera(bancada,exposicao=70000, ganho = 20, fps=200)
camera.conectar()


thread1 = threading.Thread(target = camera.filme)
thread1.start()


cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
cv2.resizeWindow('Frame', 1280, 720)

data = []
output_dir = 'frames'
i = 0
while True:
    try:


   
        img = camera.array
        #img= cv2.applyColorMap(camera.array, cv2.COLORMAP_PLASMA)
        resized_frame = cv2.resize(img, (1000, 1000))
        frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(output_dir, f'frame_{i:04d}.png'), frame)

        data.append(round(np.mean(img),2))
        print(np.mean(img))
        cv2.imshow('Frame',img)
        i+=1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.movie=False
            break
        
        
    except Exception as e:
        camera.movie=False
        print(e)
        print(camera.array,camera.array.shape)
        print('Medida falhou')

cv2.destroyAllWindows()
os.system(f'ffmpeg -r 30 -i frames/frame_%04d.png -c:v libx265 -vf fps=30 -crf 28 -preset slow -tune fastdecode -pix_fmt yuv420p -s 1280x720 -movflags +faststart output.mp4')
for file_name in os.listdir(output_dir):
    file_path = os.path.join(output_dir, file_name)
    os.remove(file_path)

plt.plot([x for x in range(len(data))],data)
plt.show()