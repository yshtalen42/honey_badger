#!/afs/slac.stanford.edu/g/ad/simul/venv/bin/pytho
import epics
import time

quad = {'1': "01G-QSS4:CurrSetpt", '2' : "02G-QSS3:CurrSetpt", '5' : "05G-QSS3:CurrSetpt", '7' : "07G-QSS2:CurrSetpt", '8' : "08G-QSS2:CurrSetpt", '9' : "09G-QSS1:CurrSetpt", '10' : "10G-QSS4:CurrSetpt", '11' : "11G-QSS3:CurrSetpt", '12' : "12G-QSS3:CurrSetpt", '14' : "14G-QSS2:CurrSetpt", '16' : "16G-QSS2:CurrSetpt", '17' : "17G-QSS2:CurrSetpt", '18' : "18G-QSS1:CurrSetpt"}

while True:
    #poll for ocelot_busy flag
    with open('ocelot_status.txt', 'r') as f:
        ocelot_busy=f.read().strip('\n')
        print('Ocelot status is: ', ocelot_busy)
    #if ocelot is busy keep polling
    if ocelot_busy=='1':
        print('ocelot is making me some set points...')
        time.sleep(5)
        continue
    #if ocelot is not busy, do the thing
    else:
        #set matlab busy flag
        with open('matlab_status.txt', 'w') as f:
            f.write('1')
        print('told ocelot I was busy...') 
        #for each quad, read the text file and print value
        x=['1', '2', '5', '7', '8', '9', '10', '11', '12', '14', '16', '17', '18']
        for i in x:
            try: 
                with open(i+'.txt', 'r') as f:
                    print('FILE: ', i+'.txt')
                    val = f.read().strip('\n')
                    print('CONTENT: ', val)
                    epics.caput(quad[i], float(val))
            except: 
                print('No quad files yet...')
        #unset matlab busy flag
        with open('matlab_status.txt', 'w') as f:
            f.write('0')
        print('told ocelot I was done...')
        time.sleep(5)
        continue



