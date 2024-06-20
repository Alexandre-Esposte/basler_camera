import numpy as np
import basler_camera as cam
import matplotlib.pyplot as plt
import cv2
import seriais
import threading
import time
import queue
import os
from utils import * 




limiar = 180
limiar_atingido = False

tempo = 10
fps = 35
buffer = queue.Queue(maxsize = tempo*fps)

width = 1216
height = 1936

serial1, serial2, serial3, bancada = seriais.NumerosSeriais()
camera = cam.Camera(bancada,exposicao=15000, ganho = 0, fps=fps)
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

        
        img, intensidade_mira, mean_intensity = aquisitar(camera)
         
        if buffer.full():
            buffer.get()

        elif limiar_atingido == False:
            buffer.put(img)

        
        # Desenhando a mira na tela
        cv2.circle(img, (936,608), 15, (255, 255, 255), 2) 

        # Desenhando na tela o valor em bits que está no centro da mira/ccd
        cv2.putText(img, f'Mira: {intensidade_mira}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, f'Global: {mean_intensity:0.2f}',   (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, f'FPS: {camera.fps_transferido:0.2f}',   (1700, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        #data.append(round(np.mean(img),2))
        
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
thread1.join()
print('Salvando Frames')
tratar_frames(buffer)

#os.system(f'ffmpeg -r {fps} -i frames/frame_%04d.png -c:v libx265 -vf fps={fps} -crf 28 -preset slow -tune fastdecode -pix_fmt yuv420p -s 1280x720 -movflags +faststart output_os.mp4')
salvar_video(fps)

for file_name in os.listdir(output_dir):
    file_path = os.path.join(output_dir, file_name)
    os.remove(file_path)

print(buffer.qsize())
