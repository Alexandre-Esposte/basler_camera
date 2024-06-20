import os
import cv2
import numpy as np
from moviepy.editor import ImageSequenceClip

output_dir = 'frames'

def aquisitar(camera):
        img = camera.array
        intensidade_mira = img[608,936]
        mean_intensity = np.mean(img)
        img= cv2.applyColorMap(camera.array, cv2.COLORMAP_TURBO)

        return img, intensidade_mira, mean_intensity



def tratar_frames(buffer):
    i = 1
    while buffer.qsize() != 0:
        img = buffer.get()
        cv2.imwrite(os.path.join(output_dir, f'frame_{i:04d}.png'), img)
        i+=1
        

def salvar_video(fps):
    

    # Obter a lista de nomes de arquivos dos frames no diretório
    frame_files = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.png')])

    # Criar o vídeo usando MoviePy
    clip = ImageSequenceClip(frame_files, fps=fps)

    # Salvar o vídeo
    clip.write_videofile('output.mp4', codec='libx264', bitrate='1000k', ffmpeg_params=['-crf', '28'])
