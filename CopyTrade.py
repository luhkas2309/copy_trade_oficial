from iqoptionapi.stable_api import IQ_Option
import logging
import socket
import time, json, logging, configparser
from datetime import datetime, date, timedelta
from dateutil import tz
import sys
import os


print('Email?')
email = input()

print('Senha?')
senha = input()

API=IQ_Option(str(email),str(senha))


 

def banca ():
    global API
    API.connect()
    return float(API.get_balance())
def entradas(config, entrada, direcao, timeframe):
    global API
    API.connect()
    # API = IQ_Option("sindel.plima@hotmail.com","Ls23092011")
    # check,reason = API.connect()
    status,id = API.buy_digital_spot(config['paridade'], entrada, direcao, timeframe)
    # if status:
    if status:
    	# STOP WIN/STOP LOSS
    	
        banca_att = API.get_balance()
        stop_loss = False
        stop_win = False
    	# if round((banca_att - float(config['banca_inicial'])), 2) <= (abs(float(config['stop_loss'])) * -1.0):
        if round((banca_att - float(config['banca_inicial'])), 2) <= (abs(float(config['stop_loss'])) * -1.0):
            stop_loss = True

        if round((banca_att - float(config['banca_inicial'])) + (float(entrada) * float(config['payout'])) + float(entrada), 2) >= abs(float(config['stop_win'])):
            stop_win = True

        while True:
            status,lucro = API.check_win_digital_v2(id)

            if status:
                if lucro > 0:
                    return 'win',round(lucro, 2),stop_win
                else:
                    return 'loss',0,stop_loss
                break
            
    else:
        return 'error',0,False
def configuracao():
    global API
    API.connect()
    arquivo = configparser.RawConfigParser()
    arquivo.read('config.txt')
    banca = API.get_balance()
    return {'seguir_ids': arquivo.get('GERAL', 'seguir_ids'),'stop_win': arquivo.get('GERAL', 'stop_win'), 'stop_loss': arquivo.get('GERAL', 'stop_loss'), 'payout': 0, 'banca_inicial': banca, 'filtro_diferenca_sinal': arquivo.get('GERAL', 'filtro_diferenca_sinal'), 'martingale': arquivo.get('GERAL', 'martingale'), 'sorosgale': arquivo.get('GERAL', 'sorosgale'), 'niveis': arquivo.get('GERAL', 'niveis'), 'filtro_pais': arquivo.get('GERAL', 'filtro_pais'), 'filtro_top_traders': arquivo.get('GERAL', 'filtro_top_traders'), 'valor_minimo': arquivo.get('GERAL', 'valor_minimo'), 'paridade': arquivo.get('GERAL', 'paridade'), 'valor_entrada': arquivo.get('GERAL', 'valor_entrada'), 'timeframe': arquivo.get('GERAL', 'timeframe'), 'payout_minimo': arquivo.get('GERAL', 'payout_minimo')}
def entradaV2_digital(par,entrada,direcao,timeframe):
    global API
    
    check,reason = API.connect()
    status,id = API.buy_digital_spot(par, entrada, direcao, timeframe)
    if check :
        if status:
        	while True:
        		status,lucro = API.check_win_digital_v2(id)
        		if status:
        			if lucro > 0:		
        				return 'win',round(lucro, 2)
        			else:				
        				return 'loss',round(float(entrada)*-1,2)
        			break
                
                
        else:
        	return 'error',0,False
    else:
        print ('Conexao Falhou')
        return 'error',0,False
def filtro_ranking(config):
    global API
    ranking = API.get_leader_board('Worldwide' if config['filtro_pais'] == 'todos' else config['filtro_pais'].upper(),1,int(config['filtro_top_traders']),0)
    user_id = []
    for n in ranking['result']['positional']:
        
        id = ranking['result']['positional'][n]['user_id']
        user_id.append(id)

    return user_id 
def martingale(tipo,valor,payout):
    if tipo == 'simples':
        final = valor * 2.2
        return final
    else:
        lucro_esperado = float(valor) * float(payout)
        perca=valor
        while True:
            if round(float(valor)*float(payout),2)> round(abs(float(perca))+float(lucro_esperado), 2):
                return round(valor,2)
                break
            valor += 0.01
def payout(par,tipo,timeframe=1):
    global API
    if tipo == 'turbo':
        a = API.get_all_profit()
        return int(100*a[par]['turbo'])
    elif tipo == 'digital':
        API.subscribe_strike_list(par,timeframe)
        while True:
            d = API.get_digital_current_profit(par,timeframe)
            if d != False:
                d = int(d)
                break
            time.sleep(1)
        API.unsubscribe_strike_list(par,timeframe)
        return d
def timestamp_converter(x, retorno = 1):
    hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora=hora.replace(tzinfo=tz.gettz('GMT'))
    return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6] if retorno == 1 else hora.astimezone(tz.gettz('America/Sao Paulo'))
def menu(paridade,timeframe):
    os.system('cls' if os.name == 'nt' else 'clear')
    global lucro_prejuizo
    banca_inicial = banca()
    print ('___________ COPY TRADE (LUCAS FEITOSA) ___________')
    print ('__________Configurações - '+str(paridade)+' ('+timeframe+')___________')
    print (' - Entrada = '+str(config['valor_entrada']))
    print (' - Martingale? = '+str(config['martingale']))
    if str(config['martingale']) == 'S':
        print (' - Niveis do Martingale = '+str(config['niveis']))
    print ('FILTROS:')
    print (' - Valor Minimo = '+str(config['valor_minimo']))
    print (' - Ranking = Top '+str(config['filtro_top_traders']))
    print (' - País = '+str(config['filtro_pais']))
    print ('Seguindo: '+str(config['seguir_ids']))
    print ('Banca atual: '+str(banca_inicial))
    print ('Lucro/prejuizo: '+str(lucro_prejuizo))
    return 0

# ABRIR CONEXAO COM IQ OPTION
config = configuracao()
API.connect()

# MENU INICIAL
tempo = ''
print('Deseja usar o arquivo de configuracao(0-Sim 1-Nao)?')
decisao = input()
if(decisao == str(1) ):
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Qual o Ativo que deseja copiar?')
    paridade = input()
    print('Quanto tempo de timeframe(1,5 ou 15)?')
    tempo = input()
    timeframe = 'PT'+tempo+'M' #PT5M #PT15M

else:
    paridade = config['paridade']
    tempo = str(config['timeframe'])
    timeframe = 'PT'+config['timeframe']+'M' #PT5M #PT15M

# BANCA INICIAL
# banca_inicial = banca()
# CHAMANDO O PAINEL
lucro_prejuizo = 0
menu(paridade,timeframe)


# BUSCANDO OS FILTROS DOS TOP TRADERS
filtro_top_traders = filtro_ranking(config)


if config['seguir_ids'] != '':
    if ',' in config['seguir_ids']:
        x = config['seguir_ids'].split(',')
        for old in x:
            filtro_top_traders.append(int(old))
    else:
        filtro_top_traders.append(int(config['seguir_ids']))
# Filtros
# 1? Filtro por valor da entrada copiada
# 2? Filtro para copiar entrada dos top X 
# 3? Filtro Pais



# AULA 2
tipo = 'live-deal-digital-option' #live-deal-binary-placed



old = 0
API.subscribe_live_deal(tipo,paridade,timeframe,10)

# Captura o Payout
config['payout'] = float(payout(paridade, 'digital', int(tempo)) / 100)
    
while True:
    
    API.subscribe_live_deal(tipo,paridade,timeframe,10)
    trades = API.get_live_deal(tipo,paridade,timeframe)
    if int(config['payout_minimo'])<=int(config['payout']*100):
        if len(trades) > 0 and trades[0]['user_id'] != old and trades[0]['amount_enrolled'] >= float(config['valor_minimo']):
            ok = True

                   # Correcao de bug em relacao ao retorno de datas errado
            res = round(time.time() - datetime.timestamp(timestamp_converter(trades[0]['created_at']/1000, 2)),2)
            ok=True if res<=int(config['filtro_diferenca_sinal']) else False


            if len(filtro_top_traders) > 0:
                if trades[0]['user_id'] not in filtro_top_traders:
                    ok = False



            if ok:
                # DADOS SINAIS
    
                print(res, end='')
                print(' [',trades[0]['flag'],']',paridade,'/',trades[0]['amount_enrolled'],'/',trades[0]['instrument_dir'],'/',trades[0]['name'],trades[0]['user_id'])

                # 1 ENTRADA
                try:
                    resultado,lucro = entradaV2_digital(paridade,config['valor_entrada'],trades[0]['instrument_dir'],int(tempo))
                    API.clear_live_deal(tipo,paridade,timeframe,2)
                    print ('     ->', resultado)

                    if resultado == 'win':
                        lucro_prejuizo = lucro_prejuizo + lucro
                    # MARTINGALE
                    if resultado == 'loss' and config['martingale'] == 'S':
                        lucro_prejuizo = lucro_prejuizo + lucro
                        valor_entrada = martingale('auto',float(config['valor_entrada']),float(config['payout']))
                        for i in range(int(config['niveis']) if int(config['niveis']) > 0 else 1):
                            resultado,lucro_martingale = entradaV2_digital(paridade,float(valor_entrada),trades[0]['instrument_dir'],int(tempo))
                            print('   MARTINGALE NIVEL '+str(i+1)+'..', end='')
                            print ('     ->', resultado)

                            if resultado == 'win':
                                print('\n')
                                lucro_prejuizo = lucro_prejuizo + lucro_martingale
                                break
                            else:
                                valor_entrada = martingale('auto',float(valor_entrada),float(config['payout']))
                                lucro_prejuizo = lucro_prejuizo + lucro_martingale




                    elif resultado == 'loss' and config ['sorosgale'] == 'S':
                        pass
                except ValueError:
                    print ('IQOptions recusou a entrada!')
                    menu(paridade,timeframe)
                    pass 
                
                
            old = trades[0]['user_id']
            menu(paridade,timeframe)
            # for contador in List(trades):
            #     index = 0
            #     del trades[index]
            #     index = index + 1
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('O valor do payout minimo('+str(config['payout_minimo'])+') não foi atingido.')
        print('['+paridade+'] - '+str(round(config['payout']*100,2)))
        print('Tentaremos novamente em 25 segundos')
        config['payout'] = float(payout(paridade, 'digital', int(tempo)) / 100)
        time.sleep(25)
        
API.unscribe_live_deal(tipo,paridade,timeframe)
        
