import numpy as np
from pypylon import pylon
import threading



class Camera():
    """A classe sensor é responsável por fazer a conexão com a câmera e todas as ações relacionadas a câmera"""

    def __init__(self,numero_serial: int = None, exposicao: int = 5000, ganho: int = 0, fps: float = 40):

        

        self.numero_serial = numero_serial # numero serial de cada camera (identificador unico)

        self.exposicao = exposicao # define a exposição da camera em microsegundos

        self.ganho = ganho # define o ganho da camera

        self.fps = fps # Define o frame rate

        self.width = 0 # comprimento

        self.height = 0 # largura
        
        self.array = np.array([]) # Essa variável armazenara a matriz de intensidades, dessa forma podemos obter a imagem amostrada

        self.fps_aquisitado = None

        self.fps_transferido = None

    
        self.tl_factory = pylon.TlFactory.GetInstance() # Coisas da pylon

        self.devices = self.tl_factory.EnumerateDevices() # Obtem cameras conectadas ao computador

        self.camera = None # Variavel que contem a instancia da camera

        self.movie = False # apenas uma flag para finalizar a filmagem



    # Métodos para conexão 

    def _determinar_device(self):
        """Determina a camera correta a ser detectada atraves do numero serial"""

        for device_info in self.devices:
            if int(device_info.GetSerialNumber()) == self.numero_serial:
                return device_info
        return False

    
    def conectar(self):
        """Conecta uma das cameras ligadas no usb atraves do numero serial informado"""

        desired_device = self._determinar_device()

        if desired_device == False:
            print("Conexao falhou: Verifique se o numero serial esta correto, camera nao encontrada\n")
            return 


        try:
            self.camera = pylon.InstantCamera(self.tl_factory.CreateDevice(desired_device))
            print("Conexao realizada com sucesso")


            if self._configuracoes():
                print('Camera configurada com sucesso')
                
            else:
                print('Falha na configuracao')
                
            
            

        except:
            print('Conexao falhou: Verifique se a camera esta conectada corretamente')
            

    
    # Métodos para abrir e fechar a camera

    
    def _verificar_status(self):
        """Verifica o status da camera: True se aberta e False se Fechada"""

        return self.camera.IsOpen()


    def _abrir_camera(self):
        """Abre a camera"""
        
        try: 
            self.camera.Open()

            return True

        except:
            return False

    def _fechar_camera(self):
        """Fecha a camera"""

        try:
            self.camera.StopGrabbing()
            self.camera.Close()
            return True

        except:
            return False


    # Configurando atributos

    def _configuracoes(self):
        '''Está função realiza a configuração de alguns parametros da camera'''

        # Aqui é necessário abrir a camera para configurar os parametros
        self._abrir_camera()
        
        try:
            
            # Quantidade de bits utilizado para armazenar as intensidades na matriz
            self.camera.PixelFormat.SetValue('Mono12')
            
            # Configurando quantidade de pixels que vamos usar nas linhas e colunas
            max_width = self.camera.WidthMax.GetValue()
            max_height = self.camera.HeightMax.GetValue()
            self.camera.Width.SetValue(max_width)
            self.camera.Height.SetValue(max_height)
            self.width = self.camera.Width.GetValue()
            self.height = self.camera.Height.GetValue()
            # Configurando o tempo de exposição
            self.camera.ExposureAuto.SetValue('Off')
            self.camera.ExposureTime.SetValue(self.exposicao)
            # Configurando o ganho
            self.camera.GainAuto.SetValue('Off')
            self.camera.Gain.SetValue(self.ganho)
            # Configurando o gamma
            self.camera.Gamma.value = 1

            
            self.camera.DeviceLinkThroughputLimitMode.SetValue('Off') # Mudar isso caso o barramento usb não suporte

            #self.camera.AcquisitionFrameRateEnable.SetValue(True) # em algumas cameras nao funciona

            
            self._fechar_camera()
                
            return True
        except Exception as err:
            self._fechar_camera()
            print(f"Erro: {err}")
            return False

    
    # Metodos para realizar as medidas

    def _ObterIntensidade(self) -> float:
        '''Este método se conectará à camera e retornará a matriz de intensidades medida pelo cmos'''

        
		# Capturar uma imagem
        self.camera.StartGrabbing()
		
        image = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

		# Converter a imagem para um array numpy
        img_array = image.Array

		
	    # Liberar a imagem
        image.Release()

        self.camera.StopGrabbing()
		
    
        self.array = img_array

        intensidade_processada = self._ProcessarMatrizIntensidade(img_array)

        

        return intensidade_processada


    def _ProcessarMatrizIntensidade(self,matriz: np.ndarray) -> float:
	
        media = matriz.mean()
		
        return media
		
                
    def _Amostragem(self, tamanho_amostra: int = 10, qt_amostras: int = 12) -> int:
        
        medida = []  
        for i in range(qt_amostras):
            medias_amostrais = []
            for j in range(tamanho_amostra):
                m = self._ObterIntensidade()
                medias_amostrais.append(m)   
            medida.append(np.array(medias_amostrais).mean())
		
        return np.array(medida).mean()

    def medir(self,tam_amostra: int = 10, qt_amostra: int = 12) -> float:

        self._abrir_camera()
         
        intensidade_media_frame = self._Amostragem(tamanho_amostra=tam_amostra, qt_amostras = qt_amostra)

        self._fechar_camera()
        
        return intensidade_media_frame


    def foto(self):
        self._abrir_camera()

        self.camera.StartGrabbing()

        frame = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

	# Converter a imagem para um array numpy
        img_array = frame.Array

		
	# Liberar a imagem
        frame.Release()

        self.camera.StopGrabbing()
		
        self.array = img_array

        self._fechar_camera()


    # ----- Métodos para filmagens ------

    def filme(self,tempo = 10):
        
        self._abrir_camera()
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        self.camera.AcquisitionFrameRate.SetValue(self.fps)

        #Permitir que a câmera ajuste automaticamente a exposição, etc.
        #self.camera.ExposureAuto.SetValue("Continuous")

        self.movie=True
        while self.movie:

            self.fps_transferido = self.camera.BslResultingTransferFrameRate.GetValue()
            self.fps_aquisitado  = self.camera.BslResultingAcquisitionFrameRate.GetValue()
            frame = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            self.array = frame.Array

            frame.Release()
        
        self.camera.StopGrabbing()
        self._fechar_camera()

        return 

    # Obter temperatura    

    def getTemperatura(self):
        self._abrir_camera()
        temperatura = self.camera.DeviceTemperature.GetValue()
        self._fechar_camera()
        return temperatura
