#!/afs/slac.stanford.edu/g/ad/simul/venv/bin/pytho
import epics
import time

quad = {'1': "01G-QSS4:CurrSetpt", '2' : "02G-QSS3:CurrSetpt", '5' : "05G-QSS3:CurrSetpt", '7' : "07G-QSS2:CurrSetpt", '8' : "08G-QSS2:CurrSetpt", '9' : "09G-QSS1:CurrSetpt", '10' : "10G-QSS4:CurrSetpt", '11' : "11G-QSS3:CurrSetpt", '12' : "12G-QSS3:CurrSetpt", '14' : "14G-QSS2:CurrSetpt", '16' : "16G-QSS2:CurrSetpt", '17' : "17G-QSS2:CurrSetpt", '18' : "18G-QSS1:CurrSetpt"}
readback = {'1': "01G-QSS4:Curr1", '2' : "02G-QSS3:Curr1", '5' : "05G-QSS3:Curr1", '7' : "07G-QSS2:Curr1", '8' : "08G-QSS2:Curr1", '9' : "09G-QSS1:Curr1", '10' : "10G-QSS4:Curr1", '11' : "11G-QSS3:Curr1", '12' : "12G-QSS3:Curr1", '14' : "14G-QSS2:Curr1", '16' : "16G-QSS2:Curr1", '17' : "17G-QSS2:Curr1", '18' : "18G-QSS1:Curr1"}

while True:
    #poll for ocelot_busy flag
    with open('ocelot_status.txt', 'r') as f:
        ocelot_busy=f.read().strip('\n')
        f.close()
    print('Ocelot status is: ', ocelot_busy)
    #if ocelot is busy keep polling
    if ocelot_busy=='1':
        print('ocelot is making me some set points...')
        time.sleep(0.5)
        continue
    #if ocelot is not busy, do the thing
    else:
        #set matlab busy flag
        with open('matlab_status.txt', 'w') as f:
            f.write('1')
            f.close()
        print('told ocelot I was busy...') 
        #for each quad, read the text file and print value
        x=['1', '2', '5', '7', '8', '9', '10', '11', '12', '14', '16', '17', '18']
        for i in x:
            try: 
                print('FILE: ', i+'.txt')
                with open(i+'.txt', 'r') as f:
                    val = f.read().strip('\n')
                    f.close()
                print('CONTENT: ', val)
                epics.caput(quad[i], float(val))
                epics.caput(readback[i], float(val))
            except: 
                print('No quad files yet...')
        #unset matlab busy flag
        with open('matlab_status.txt', 'w') as f:
            f.write('0')
            f.close()
        print('told ocelot I was done setting devices...\n\n')
        time.sleep(0.5)
        continue



