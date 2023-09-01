from PySimpleGUI import PySimpleGUI as sg
import json
import time
import sys

#lendo parametros
parametros = sys.argv[1:]
nome_file = ''
if(len(parametros) > 1):
    print("ERRO: Programa espera 1 ou nenhum parametro, mas recebeu "+ str(len(parametros))+ ".")
    exit()
elif(len(parametros) == 1):
    nome_file = sys.argv[1]
else:
    nome_file = "setupla.json"

#lendo arquivo json com a septupla da maquina
with open(nome_file) as file:
    setupla = json.load(file)

pausa_auto = 0.1 #segundos
pos_atual = 0
estado_atual = setupla["estado_inicial"]
nome = setupla['nome']
etapas = 0

def avancar(auto):
    global estado_atual
    global etapas
    
    print("\nEtapa atual: " + str(etapas))
    print("Estado atual: ", estado_atual,"Simbolo atual: ", fita[pos_atual])

    if fita[pos_atual] in setupla['transicoes'][estado_atual]: #ainda existem transições
        [proximo_estado, sim_gravar, direcao] = setupla['transicoes'][estado_atual][fita[pos_atual]]
        print("Próximo estado: ", proximo_estado)
        print("Simbolo a gravar: ", sim_gravar)
        print("Direção para mover a fita: ", direcao)

        if (((proximo_estado in setupla['estados']) == False) or ((sim_gravar in setupla['simbolos_fita']) == False)):
            if (proximo_estado in setupla['estados']) == False:
                janela['entrada'].update('Estado ' + proximo_estado +  ' não existente na especificação da MT!')
            if (sim_gravar in setupla['simbolos_fita']) == False:
                mensagem = 'Símbolo ' + sim_gravar +  ' não existente na especificação da MT!'
                janela['entrada'].update(mensagem)
            
            janela['Avançar'].update(disabled = True)
            janela['Auto'].update(disabled = True)
            return

        estado_atual = proximo_estado
        etapas += 1
        janela['text_estado'].update(estado_atual)
        janela['etapas'].update(etapas)
        simbolo_antigo = fita[pos_atual]
        grava_fita(sim_gravar)
        janela.refresh()

        if(auto == False):
            if(simbolo_antigo != sim_gravar):
                while(True):
                    eventos, valores = janela.read()
                    if(eventos == 'Avançar' or eventos == sg.WIN_CLOSED):
                        break
        else:
            time.sleep(pausa_auto)

        if(direcao == '<'):
            move_fita_esquerda()
        elif(direcao == '>'):
            move_fita_direita()
        else:
            print('Simbolo de direcao inválido')
    
    else: #não existem mais transições
        janela['Avançar'].update(visible = False)
        janela['Auto'].update(visible = False)
        janela['Resetar'].update(visible = True)

        if(setupla['aceitacao']):
            if(estado_atual in setupla['estados_finais']):
                janela['Parou'].update('MT parou! Entrada aceita!', text_color = 'green', visible = True)
            else:
                janela['Parou'].update('MT parou! Entrada rejeitada!', text_color = 'red', visible = True)
        else:
            fita_final = ''
            for x in fita:
                fita_final += x
            
            fita_final = fita_final.strip(setupla['simbolo_branco'])
            fita_final = 'Saida final: ' + fita_final
            janela['Parou'].update('MT Parou!', visible = True)
            janela['saida'].update(fita_final, visible = True)

def resetar():
    global estado_atual
    global pos_atual
    global fita
    global etapas
    estado_atual = setupla['estado_inicial']
    pos_atual = 0
    fita = []
    etapas = 0
    desenha_fita()
    janela['Carregar'].update(visible = True)
    janela['entrada'].update(disabled = False)
    janela['Avançar'].update(visible = True, disabled = True)
    janela['Auto'].update(visible = True, disabled = True)
    janela['saida'].update(visible = False)
    janela['Parou'].update(visible = False)
    janela['Resetar'].update(visible = False)
    janela['text_estado'].update('')

# GUI --------------------------------------------------------------------------------------------------
def desenha_fita():
    for i in range(0,tamFita):
        if( i + pos_atual - pos_leitura >= 0 and i + pos_atual - pos_leitura < len(fita)): 
            janela[i].update(fita[i + pos_atual - pos_leitura])
        else:
            janela[i].update(setupla['simbolo_branco'])
    print("Posição atual = ", pos_atual)

def move_fita_direita():
    global pos_atual 
    pos_atual += 1
    if(pos_atual == len(fita)):
        fita.append(setupla['simbolo_branco'])
    desenha_fita()

def move_fita_esquerda():
    global pos_atual
    if(pos_atual == 0):
        fita.insert(0, setupla['simbolo_branco'])
    else:
        pos_atual -= 1
    desenha_fita()

def grava_fita(valor):
    fita[pos_atual] = valor
    desenha_fita()

#Layout da janela
#sg.theme('LightBrown11')
sg.theme('LightGreen4')
fonte_titulo = ('Courier New', 20, 'bold')
fonte_subtitulo = ('Courier New', 18, 'bold')
fonte_padrao = ('Courier New', 14, 'bold')
tamFita = 21
pos_leitura = tamFita//2

botao = [sg.InputText('', disabled=True, key = i, size = 2, font = fonte_titulo, justification='center', text_color = 'black') for i in range(0,tamFita)]

layout = [
    [sg.Text('Máquina de Turing', font = fonte_titulo)],
    [sg.Text('', font = fonte_subtitulo, key = 'nome')],
    [sg.Text('Entrada:', key = 'texto_entrada', font = fonte_padrao), sg.InputText(size=60, key = 'entrada', font = fonte_padrao), sg.Button('Carregar', font = fonte_padrao)],
    [sg.Text('∨', font = fonte_padrao)],
    [botao],
    [sg.Text('∧', font = fonte_padrao)],
    [sg.Text('Estado atual:', font = fonte_subtitulo), sg.Text('', key='text_estado', font = fonte_subtitulo), sg.Text('Etapas:', font = fonte_subtitulo), sg.Text('0', key = 'etapas', font = fonte_subtitulo)],
    [sg.Button('Avançar', font= fonte_padrao, disabled = True), sg.Button('Auto', font = fonte_padrao, disabled = True), sg.Text(key = 'Parou', font = fonte_subtitulo), sg.Text('Fita final: ', visible = False, key = 'saida', font = fonte_subtitulo)],
    [sg.Button('Resetar', font = fonte_padrao, visible = False)]
]

#Janela
janela = sg.Window('Maquina de Turing', layout, element_justification = 'c', finalize= True, size = (1000,350))
janela['nome'].update(nome)
if((estado_atual in setupla['estados']) == False):
    janela['entrada'].update("Estado inicial inválido!", disabled = True, text_color = 'black')
    janela['Avançar'].update(disabled = True)
    janela['Auto'].update(disabled = True)
    janela['Carregar'].update(disabled = True)

#Ler os eventos
while True:
    eventos, valores = janela.read()
    
    if eventos == sg.WINDOW_CLOSED:
        break
    
    if eventos == 'Carregar': 
        entrada = valores['entrada']
        fita = [entrada[i] for i in range(0,len(entrada))]
        valido = True
        for i in fita:
           valido = valido and (i in setupla['simbolos_fita'])
        valido = valido and (len(fita) != 0)

        if(valido):
            janela['Carregar'].update(visible = False)
            janela['Avançar'].update(disabled = False)
            janela['Auto'].update(disabled = False)
            janela['texto_entrada'].update('Entrada original:')
            janela['entrada'].update(disabled = True, text_color = 'black')
            janela['text_estado'].update(estado_atual)
            desenha_fita()
        else:
            janela['entrada'].update("Favor inserir somente símbolos do alfabeto de entrada!")

    if eventos == 'Avançar':
        avancar(False)

    if eventos == 'Auto':
        janela['Avançar'].update(disabled = True)

        inicio = time.time()

        while(True):
            avancar(True)
            if((fita[pos_atual] not in setupla['transicoes'][estado_atual])):
                avancar(True)
                break
            time.sleep(pausa_auto)
        
        fim = time.time()
        print("Tempo de execução:", fim-inicio)

        janela['Avançar'].update(disabled = False)
        
    if eventos == 'Resetar':
        resetar()