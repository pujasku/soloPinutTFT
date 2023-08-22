import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime,date
import time
import json

#====================================================Funciones============================================
def ligaToInt(liga):
    if (liga== 'CHALLENGER'):
        return 9
    elif(liga == 'GRANDMASTER'):
        return 8
    elif(liga == 'MASTER'):
        return 7
    elif(liga == 'DIAMOND'):
        return 6
    elif(liga == 'PLATINUM'):
        return 5
    elif(liga == 'GOLD'):
        return 4
    elif(liga == 'SILVER'):
        return 3
    elif(liga=='BRONZE'):
        return 2
    elif(liga=='IRON'):
        return 1
    else:
        return 0

def romanoToInt(num):
    if(num=='I'):
        return 1
    if(num=='II'):
        return 2
    if(num == 'III'):
        return 3
    if(num == 'IV'):
        return 4
    if(num == 'V'):
        return 5
    else:
        return 0

def plToInt(num):
    try:
        return int(num)
    except:
        return 0

def imprimirEnTabla(arr):
    row=2
    for i in arr:
        worksheet.update(f'A{row}', i['summoner'])
        worksheet.update(f'B{row}', i['tier'])
        worksheet.update(f'C{row}', i['rank'])
        worksheet.update(f'D{row}', i['leaguePoints'])
        worksheet.update(f'E{row}', round(i['prom'],2))
        row+=1

def bubbleSort(arr):
    n = len(arr)
    for i in range(0,n-1):
        swapped = False
        for j in range(0,n-i-1):
            #si es de mayor liga
            ligaArriba = ligaToInt(arr[j]['tier'])
            ligaAbajo = ligaToInt(arr[j+1]['tier'])
            if (ligaArriba < ligaAbajo):
                aux = arr[j]
                arr[j] = arr[j+1]
                arr[j+1] = aux
                swapped = True
            #si son misma liga comparo rango
            elif(ligaArriba == ligaAbajo):
                rangoArriba = romanoToInt(arr[j]['rank'])
                rangoAbajo = romanoToInt(arr[j]['rank'])
                if( rangoArriba > rangoAbajo):
                    aux = arr[j]
                    arr[j] = arr[j+1]
                    arr[j+1] = aux
                    swapped = True
                #si son misma liga mismo rango comparo pl
                elif(rangoArriba == rangoAbajo):
                    if(plToInt(arr[j]['leaguePoints']) > plToInt(arr[j]['leaguePoints'])):
                        aux = arr[j]
                        arr[j] = arr[j+1]
                        arr[j+1] = aux
                        swapped = True
        if (swapped == False):
            break

#====================================================Main prog============================================
# Ruta del archivo JSON con las credenciales
credentials_file = '/home/pujasku/Sync/projects/soloPinutTFT/googlekeys.json'

# Alcance de acceso a Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Carga las credenciales y autentica el cliente
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
client = gspread.authorize(credentials)

# Abre la hoja de cálculo
spreadsheet = client.open('SOLOPINUT TFT EDICION 2023')
worksheet = spreadsheet.sheet1

#columna en la que estan los summoners
nombres = 1
filas = worksheet.col_values(nombres)
#elimino primer elemento
filas.pop(0)

#declaro un arreglo de jugadores y otras variables
jugadores = []
#masCorta = float("inf")
#masTops = -1

fecha_inicio = date(2023, 6, 22)
fecha_act = date.today()
diff_dias = fecha_act - fecha_inicio
dias = diff_dias.days

#ahora recorro los nicknames y hago las peticiones pertinentes para saber elo y wins de cada uno

# Configura las variables necesarias
with open("riotApi.json") as file:
    riotApi = json.load(file)
api_key = riotApi["key"] 
region = 'LA2'  #la2 es las, la1 es lan

row = 1
for i in filas:
    print('>>Solicitando datos de ',i)
    row = row + 1
    # Nombre de invocador del usuario
    summonerName = i
    player = {}
    player['summoner'] = summonerName
    # Realiza una solicitud para obtener el id del invocador
    url1 = f'https://{region}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{summonerName}'
    headers = {
        'X-Riot-Token': api_key}
    response1 = requests.get(url1, headers=headers)

    # Verifica si la solicitud fue exitosa
    if response1.status_code == 200:
        print('  >credenciales de summoner obtenidas')
        summoner_data1 = response1.json()
        id = summoner_data1['id']
        puuid = summoner_data1['puuid']
        #procedo con la siguiente request
        url2 = f'https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{id}'
        headers = {
        'X-Riot-Token': api_key}
        response2 = requests.get(url2, headers=headers)
        if response2.status_code == 200:
            summoner_data2 = response2.json()
            print('  >Datos de ',summonerName,' obtenidos')
            if (summoner_data2 != []):
                player['tier'] = (summoner_data2[0])['tier']
                player['rank'] = (summoner_data2[0])['rank']
                player['leaguePoints'] = (summoner_data2[0])['leaguePoints']
            else: print('>>No habia informacion sobre ese summoner')
        else:
            print('>>Error al realizar la segunda solicitud:', response2.status_code)
        #peticion para calcular promedio de games
        url3 = f'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&startTime=1687392000&count=1000'
        response3 = requests.get(url3,headers=headers)
        if response3.status_code == 200:
            #calculo promedio games jugados
            matches = response3.json()
            player['prom'] = (len(matches)/dias)
            player['games'] = len(matches)
            #voy a iterar la lista para obtener algunas stats
        else:
            print('>>Error al realizar solicitud de games')
    else:
        print('>>Error al solicitar elo del invocador:', response1.status_code)
    jugadores.append(player)

print('>>Ordenando tabla...')
bubbleSort(jugadores)
imprimirEnTabla(jugadores)
time = "Ultima actualizacion: " + str(datetime.now())
worksheet.update(f'F{11}', time)
print('>>Tabla actualizada')
