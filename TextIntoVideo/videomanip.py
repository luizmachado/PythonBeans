mport moviepy.editor as mp
import cv2
import sys


def add_text_to_video(file_input, file_output, text):

    # Ler video
    video_input = mp.VideoFileClip(file_input)

    # Obter dimensão do vídeo
    w, h = moviesize = video_input.size
    
    #Definir fonte do texto
    my_text = mp.TextClip(text, font='Adobe Courier', color='white', fontsize=40)
    
    # Configuração do background da fonte
    txt_col = my_text.on_color(size=(my_text.w, my_text.h), color=(0,0,0), pos=('center','center'), col_opacity=0.6)
    
    # Definir posição do texto
    txt_mov = txt_col.set_position(("center","center"))
    
    # Juntar texto com vídeo
    final = mp.CompositeVideoClip([video_input,txt_mov])
    
    # Exportar vídeo
    final.subclip(0,17).write_videofile(file_output,fps=24,codec='libx264')

    
def execute_video(file_input):
    # Capturar vídeo
    video = cv2.VideoCapture(file_input)
    
    # Conferir se vídeo foi carregado
    if (video.isOpened()== False): 
      print("Erro ao abrir vídeo")
       
    # Ler enquanto houver vídeo
    while(video.isOpened()):
          
      # Capturar cada frame
      ret, frame = video.read()
      if ret == True:
       
        # Exibir frame
        cv2.imshow('Frame', frame)
       
        # Pressionar "q" para sair
        if cv2.waitKey(25) & 0xFF == ord('q'):
          break
       
      else: 
        break
       
    # Liberar objeto quando finalizar
    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    kwargs = dict(x.split('=', 1) for x in sys.argv[1:])
    
    #Definir valores padrão
    if not 'input' in kwargs:
        kwargs['input'] = ('videos/sample.mp4')
    if not 'output' in kwargs:
        kwargs['output'] = ('videos/result.mov')
    if not 'texto' in kwargs:
        kwargs['texto'] = f'Recorde atingido.\n30.000 tons'

    #Executar funções para gerar e reproduzir vídeo
    add_text_to_video(kwargs['input'], kwargs['output'], kwargs['texto'])
    execute_video(kwargs['output'])


