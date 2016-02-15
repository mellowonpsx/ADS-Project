import sys
import argparse
import time
import re
import os
import random
import math
import itertools

tempFileIn = None
tempFileOut = None

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

class Cone:
    def __init__(self, name, status,inputs):
        self.name = name
        self.status = status
        self.inputs = []
        self.inputs.extend(inputs)

def checkParams():
    req_version = (3,4)
    cur_version = sys.version_info
    if cur_version < req_version:
        print('Require version <= 3.4, please consider upgrading.', file=sys.stderr)
        exit(-1)

    parser = argparse.ArgumentParser(description='Diagnosi Circuito by @Sergio L.')
    parser.add_argument('-i', '--input', metavar='filename', required=True, help='input file, contiene il circuito output di simulazione.py', type=argparse.FileType('r'))
    parser.add_argument('-s', '--smart_redux', required=False, action='store_true', help='flag di riduzione configurazioni (algoritmo pagina 17)')
    parser.add_argument('-o', '--output', metavar='filename', required=True, help='output file', type=argparse.FileType('w'))
    parser.add_argument('-t', '--tempin', metavar='filename', required=True, help='temp file usato per il passaggio dati a staccato', type=argparse.FileType('a+'))
    parser.add_argument('-u', '--tempout', metavar='filename', required=True, help='temp file di output di staccato (il file deve esistere!)', type=argparse.FileType('r'))
    #parser.add_argument('--all_diagnoses', required=False, action='store_true', help='flag per diagnosi completa')
    parser.add_argument('--diagnoses_without_masking', required=False, action='store_true', help='flag per diagnosi senza mascheramento')
    parser.add_argument('--diagnoses_one_config', required=False, type=int, help='flag per diagnosi senza mascheramento')
    parser.add_argument('--diagnoses_one_choice', required=False, type=int, help='flag per diagnosi senza mascheramento')
    #parser.add_argument('-a', '--all_diagnoses', metavar='filename', help='file confgirazione/scelta diagnosi', type=argparse.FileType('r'))
    #parser.add_argument('-d', '--diagnoses_one_config', metavar='filename', help='file confgirazione/scelta diagnosi', type=argparse.FileType('r'))
    #parser.add_argument('-d', '--diagnose', metavar='[all_diagnoses, senza_mascheramento, diagnoses_one_config, diagnoses_one_choice]', default='all_diagnoses',
    #                    choices=['all_diagnoses', 'diagnoses_without_masking', 'diagnoses_one_config', 'diagnoses_one_choice'])
    args = parser.parse_args()
    return args

def MHS(A, B):
    BMatrix = []
    #BList = list(set(itertools.chain(*B)))
    #BList.sort(key=natural_keys)
    #for row in B:
    #    BRow = []
    #    for cell in BList:
    #        if cell in row:
    #            BRow.append('1')
    #        else:
    #            BRow.append('0')
    #    BMatrix.append(BRow)
    AList = list(set(itertools.chain(*A)))
    AList.sort(key=natural_keys)
    #print("B:",B,"Alist:",AList)
    for row in B:
        BRow = []
        for cell in AList:
            if cell in row:
                BRow.append('1')
            else:
                BRow.append('0')
        BMatrix.append(BRow)

    #print("BMatrix: ", BMatrix)
    global tempFileIn
    global tempFileOut
    if len(BMatrix) > 0:
        tempFileIn.seek(0)
        tempFileIn.truncate()
        for line in BMatrix:
            for cell in line:
                print(int(cell), file=tempFileIn, end=' ')
            print('-', file=tempFileIn)
        tempFileIn.flush()
        command = 'staccato.exe -o '+str(len(AList))+' '+str(tempFileIn.name)+' > '+str(tempFileOut.name)
        if os.name=='posix':
            command = './staccato.nix -o '+str(len(AList))+' '+str(tempFileIn.name)+' > '+str(tempFileOut.name)
        result = os.system(command)
        print("\t\t\tcall:",command, "result:", result)
        tempFileOut.seek(0)
        minimalHS = []
        for line in tempFileOut:
            Bset = []
            tokens = re.split('\W+', line)
            tokens = [x[1:] for x in tokens if x]
            for token in tokens:
                element = AList[int(token)-1]
                if element not in Bset:
                    Bset.append(element)
            minimalHS.append(Bset)
            #print("MHS:", minimalHS)
        return minimalHS
    return []

def diagnoses_one_choice(A, s):
    B = []
    #print("scelta: ",s)
    #print("A: ",A)
    h = []
    for (i,j) in s:
        ISi_not_Cj = []
        ISi_and_Cj = []
        if i < len(A) and i >= len(A):
            ISi_not_Cj = [x for x in A[i]]
        elif i < len(A) and j < len(A):
            ISi_not_Cj = [x for x in A[i] if x not in A[j]]
            ISi_and_Cj = [x for x in A[i] if x in A[j]]

        #print("IS"+str(i)+"\\C"+str(j)+":", ISi_not_Cj)
        #print("IS"+str(i)+"anC"+str(j)+":", ISi_and_Cj)
        if len(ISi_not_Cj) <= 0 or len(ISi_and_Cj) <=0:
            return []
        else:
            B.append(ISi_not_Cj)
            B.append(ISi_and_Cj)
        h.append(j)

    for i in range(len(A)):
        if i not in h:
            B.append(A[i])

    print("\t\tB:", B)
    mhs = MHS(A, B)
    print("\t\tMHS:", mhs)
    return mhs

def main():
    args = checkParams()
    inputFile = args.input
    outputFile = args.output
    riduciCombinazioni = args.smart_redux
    #riduciCombinazioni = False
    global tempFileIn
    global tempFileOut
    tempFileIn = args.tempin
    tempFileOut= args.tempout

    #inputFileName = os.path.splitext(inputFile.name)[0]

    cones = []
    for line in inputFile:
        line = line.strip()
        if line.strip() != '':
            #print("linea: ", line)
            isOutput = re.match('^OUTPUT', line)
            if isOutput is not None:
                continue

            isCone = re.match('^CONO', line)
            if isCone is not None:
                tokens = re.split('\W+', line)
                tokens = [x for x in tokens if x]
                #tokens[0] = 'CONO', tokens[1] = 'gate name', tokens[2] = 'status', tokens[3] = 'gate name(again)', tokens[4:] = 'other gate names'
                #print('cono:',tokens[1],', status:',tokens[2],', gate coinvolti: ',tokens[4:])
                cones.append(Cone(tokens[1],tokens[2],tokens[4:]))

    #print([(cone.name, cone.status, cone.inputs) for cone in cones if cone])

    #slide 17, è un vero miglioramento?
    #nel caso in cui il mascheramento sia un fenomeno locale di un solo cono?
    #riduciCombinazioni = True
    if riduciCombinazioni is True:
        gatesKO = []
        for cone in cones:
            if cone.status == 'KO':
                gatesKO.extend(cone.inputs)

        for cone in cones:
            if cone.status == 'OK':
                safeGate = True
                for gate in cone.inputs:
                    if gate in gatesKO:
                        safeGate = False
                if safeGate is True:
                    cone.status = 'OKS'

    non_masking_config = [cone.status for cone in cones if cone]
    #print(non_masking_config)

    numOk = sum(x == 'OK' for x in non_masking_config)
    allCombinations = itertools.product('OM', repeat=numOk)

    #print([x for x in allCombinations])

    #allDiagnoses
    #generateAllConfiguration
    allConfiguration = []
    for combination in allCombinations:
        cfg = []
        for element in non_masking_config:
            if element == 'KO':
                cfg.append('KO')
            elif element == 'OKS':
                cfg.append('OK')
            else:
                cfg.append('OKM' if combination[0]=='M' else 'OK')
                combination = combination [1:]
        allConfiguration.append(cfg)

    #print([x for x in allConfiguration])
    #return

    if args.diagnoses_without_masking and (args.diagnoses_one_config is not None):
        print("Errore flag incompatibili: diagnoses_without_masking and diagnoses_one_config")
        return
    elif args.diagnoses_without_masking:
        allConfiguration = [allConfiguration[0]]

    if args.diagnoses_one_config is not None and args.diagnoses_one_config>=0 and args.diagnoses_one_config < len(allConfiguration):
        allConfiguration = [allConfiguration[args.diagnoses_one_config]]
    elif args.diagnoses_one_config:
        print("Errore flag diagnoses_one_config, valore non valido: ", args.diagnoses_one_config)
        return

    print('Ci sono:', len(allConfiguration),'combinazioni')
    print('Ci sono:', len(allConfiguration),'combinazioni', file=outputFile)

    numConfig = 1
    for configuration in allConfiguration:
        print('configurazione [', numConfig,'/', len(allConfiguration),']:', configuration)
        print('configurazione [', numConfig,'/', len(allConfiguration),']:', configuration, file=outputFile)
        numConfig += 1

        #uISy si indica l’unione di tutti i coni relativi a uscite che in vi assumono il valore OK
        uISy = []
        for i in range(len(configuration)):
            if configuration[i] == 'OK':
                uISy.extend(cones[i].inputs)

        #A is Collection of all ISx\(uISy), Cz = Cz\(uISy)
        A = []
        _ISx = []
        _Cz = []
        for i in range(len(configuration)):
            if configuration[i] == 'OKM':
                ISx = [cones[i].name]
                ISx.extend([gate for gate in cones[i].inputs if gate not in uISy])
                #print('temp:',ISx)
                _ISx.append(ISx)
                A.append(ISx)
            if configuration[i] == 'KO':
                Cz = [cones[i].name]
                Cz.extend([gate for gate in cones[i].inputs if gate not in uISy])
                _Cz.append(Cz)
                #print('temp:',Cz)
                A.append(Cz)

        #print("A: ", A)

        indexOfOKM = [i for i in range(len(configuration)) if configuration[i] == 'OKM']
        indexOfAllNotKO = [i for i in range(len(configuration)) if configuration[i] != 'KO']
        indexOfKO = [i for i in range(len(configuration)) if configuration[i] == 'KO']

        pairs = [[i, j] for i in indexOfAllNotKO for j in indexOfKO]
        #print("pairs:", pairs)

        choices = []
        for i in range(len(indexOfOKM), len(pairs)+1):
            choices.extend([a for a in itertools.combinations(pairs, i)])

        #print("choices:", choices)

        goodChoices = []
        for choice in choices:
            numberOfKO = 0
            indexOfDistinctKO = []
            numberOfOKM = 0
            indexOfDistinctOKM = []
            indexOfOKMtoConfirm = list(indexOfOKM)
            for pair in choice:
                if pair[0] in indexOfOKMtoConfirm:
                    indexOfOKMtoConfirm.remove(pair[0])
                if pair[0] in indexOfKO and pair[0] not in indexOfDistinctKO:
                    numberOfKO+= 1
                    indexOfDistinctKO.append(pair[0])
                if pair[0] in indexOfOKM and pair[0] not in indexOfDistinctOKM:
                    numberOfOKM+= 1
                    indexOfDistinctOKM.append(pair[0])

            if len(indexOfOKMtoConfirm) <= 0 and numberOfKO <= numberOfOKM:
                goodChoices.append(choice)

        if args.diagnoses_one_choice is not None and args.diagnoses_one_choice>=0 and args.diagnoses_one_choice < len(goodChoices):
            goodChoices = [goodChoices[args.diagnoses_one_choice]]
        elif args.diagnoses_one_choice:
            print("Errore flag diagnoses_one_choice, valore non valido: ", args.diagnoses_one_choice)
            return

        #print("choices:", goodChoices)

        #print("Good choices:", goodChoices)
        print('\tCi sono:', len(goodChoices),'scelte')
        print('\tCi sono:', len(goodChoices),'scelte', file=outputFile)

        numChoice = 1
        deltai = set()
        for s in goodChoices:
            print('\t\tScelta',numChoice,'/', len(goodChoices),':')
            numChoice+=1
            _deltai = diagnoses_one_choice(A, s)
            #deltai.app_deltai = diagnoses_one_choice(_ISx, _Cz, s)
            for mhs in _deltai:
                deltai.add(str(mhs))
            #print("deltai:", _deltai)
            #if _deltai is not None:
            #    deltai.union(_deltai)
            #print("\tdeltai:", deltai)
        #print("\tdeltai:", deltai)
        if len(deltai) <= 0:
            print("\tconfigurazione non valida:", deltai)
            print("\tconfigurazione non valida:", file=outputFile)
        else:
            print("\tCi sono ",len(deltai),"possibili diagnosi: ")
            print("\t\t", deltai)
            print("\tCi sono ",len(deltai),"possibili diagnosi: ", file=outputFile)
            print("\t\t", deltai, file=outputFile)
    #print('fine configuration')
    #print('fine configuration', file=outputFile)

if __name__ == "__main__":
    main()