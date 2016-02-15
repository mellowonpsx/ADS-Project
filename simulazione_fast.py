__author__ = 'mellowonpsx'
#ref : http://whatis.techtarget.com/definition/logic-gate-AND-OR-XOR-NOT-NAND-NOR-and-XNOR

import sys
import argparse
import time
import re
import os
import random
import math

def operator_not(value):
    #!A
    return int(not value)

def operator_and(value1, value2):
    #A AND B
    return int(value1 and value2)

def operator_nand(value1, value2):
    #!(A AND B)
    return int(not(value1 and value2))

def operator_or(value1, value2):
    #A OR B
    return int(value1 or value2)

def operator_nor(value1, value2):
    #!(A OR B)
    return int(not(value1 or value2))

def operator_xor(value1, value2):
    #(A AND !B) OR (!A AND B)
    return int((value1 and not value2) or (not value1 and value2))

def operator_xnor(value1, value2):
    #(A AND B) OR (!A AND !B)
    return int(not((value1 and not value2) or (not value1 and value2)))

logic = {}
logic['NOT'] = operator_not
logic['AND'] = operator_and
logic['NAND'] = operator_nand
logic['OR'] = operator_or
logic['NOR'] = operator_nor
logic['XOR'] = operator_xor
logic['XNOR'] = operator_xnor

class Circuit():
    def __init__(self, name):
        self.name = name
        self.inputs = []
        self.outputs = []
        self.gates = {}

    def setInput(self, inputList):
        if len(inputList) != len(self.inputs):
            return 1
        else:
            self.resetUpdatedFlag();
            for index in range(len(self.inputs)):
                self.inputs[index].setOutput(inputList[index])
            return 0

    def addGates(self, newCone):
        self.gates[newCone.name] = newCone

    def getCone(self, coneName):
        return self.gates[coneName]

    def addInput(self, newCone):
        self.inputs.append(newCone)
        self.addGates(newCone)

    def addOutput(self, newCone):
        self.outputs.append(newCone)
        self.addGates(newCone)

    def updateValue(self):
        for this_output in self.outputs:
            this_output.updateValue()
            this_output.updateErrorValue()
        return self.updateStatus()

    def getOutputConesNO(self):
        outputCones = []
        for inputCone in self.outputs:
            thisCone = []
            thisCone.append('CONO('+inputCone.name+','+inputCone.status+')=')
            inputCones = inputCone.getInputCones2()
            thisCone.append(inputCones)
            for oneCone in inputCones:
                self.gates[oneCone].cone_updated = False
            outputCones.append(thisCone)
        return outputCones

    def getOutputCones(self):
        outputCones = []
        for inputCone in self.outputs:
            thisCone = []
            thisCone.append('CONO('+inputCone.name+','+inputCone.status+')=')
            inputCones = inputCone.getInputCones({})
            inputCones = list(inputCones)
            thisCone.append(inputCones)
            outputCones.append(thisCone)
        return outputCones

    def updateStatus(self):
        outputs = []
        for key in self.gates:
            status = '['+key+']:'+self.gates[key].updateStatus()
            outputs.append(status)
        return outputs

    def resetUpdatedFlag(self):
        for key in self.gates:
            self.gates[key].resetUpdatedFlag()

class Cone():
    def __init__(self, name, operator=None):
        self.inputs = []  #if inputs is empty, than the cone is an inputs node
        self.name = name
        self.operator = operator
        self.output = -1
        self.error_output = -1
        self.error = None
        self.updated = False
        self.error_updated = False
        self.status = None
        self.cone_updated = False

    def resetUpdatedFlag(self):
        self.updated = False
        self.error_updated = False

    def updateStatus(self):
        if self.output == self.error_output:
            self.status = 'OK'
        else:
            self.status = 'KO'
        return self.status

    def getInputCones2(self):
        if len(self.inputs) <= 0:
            return []

        if self.cone_updated == True:
            return []

        self.cone_updated = True
        cones = [self.name]
        for inputGate in self.inputs:
            inputCones = inputGate.getInputCones2()
            if inputCones is not []:
                cones.extend(inputCones)
        return cones

    def getInputCones(self, evaluated = {}):
        if len(self.inputs) <= 0:
            return {}
        else:
            if self.name not in evaluated:
                evaluated[self.name] = self.name
                for inputCone in self.inputs:
                    for thisCone in inputCone.getInputCones(evaluated):
                        evaluated[thisCone] = thisCone
            else:
                evaluated[self.name] = self.name
            return evaluated

    def getInputList(self):
        return self.inputs

    def addInput(self, newCone):
        self.inputs.append(newCone)

    def setOutput(self, newOutput):
        self.output = newOutput
        if self.error is None:
            self.error_output = newOutput

    def setError(self, error):
        self.error = error
        if error == 'stuck-to-zero':
            self.error_output = 0
            return
        if error == 'stuck-to-one':
            self.error_output = 1
            return

    def updateValue(self):
        if len(self.inputs) <= 0 or self.updated is True:
            return self.output

        result = self.inputs[0].updateValue()
        if self.operator == 'NOT':
            self.output = logic['NOT'](result)
            self.updated = True
            return self.output

        for this_input in self.inputs[1:]:
            self.output = logic[self.operator](result, this_input.updateValue())
        self.updated = True
        return self.output

    def updateErrorValue(self):
        if len(self.inputs) <= 0 or self.error_updated is True:
            return self.error_output

        result = self.inputs[0].updateErrorValue()
        if self.operator == 'NOT':
            if self.error is not None:
                self.error_updated = True
                return self.error_output
            else:
                self.error_output = logic['NOT'](result)
                self.error_updated = True
                return self.error_output
        for this_input in self.inputs[1:]:
            result = logic[self.operator](result, this_input.updateErrorValue())
        if self.error is not None:
            self.error_updated = True
            return self.error_output
        else:
            self.error_output = result
            self.error_updated = True
            return self.error_output

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def checkParams():
    req_version = (3,4)
    cur_version = sys.version_info
    if cur_version < req_version:
        print('Require version <= 3.4, please consider upgrading.', file=sys.stderr)
        exit(-1)

    parser = argparse.ArgumentParser(description='class_diagnoses by @Sergio L.')
    parser.add_argument('--input','-i', metavar='filename', required=True, help='input file, contiene il circuito in formato ISCAS85', type=argparse.FileType('r'))
    parser.add_argument('--output','-o', metavar='filename', required=True, help='output file', type=argparse.FileType('w'))
    parser.add_argument('--test','-t', metavar='filename', required=True, help='test file', type=argparse.FileType('a+'))
    parser.add_argument('--error','-e', metavar='filename', required=True, help='error file', type=argparse.FileType('a+'))
    parser.add_argument('--error_rate','-r',  metavar='[0-100]', required=False, help='error rate file', default=0, type=int, choices=range(0,101))
    parser.add_argument('--generate', required=False, action='store_true', help='flag to generate test and error file')
    args = parser.parse_args()
    return args

def main():
    args = checkParams()
    inputFile = args.input
    inputFileName = os.path.splitext(inputFile.name)[0]
    outputFile = args.output
    testFile = args.test
    errorFile = args.error
    errorRate = args.error_rate
    generateFiles = args.generate

    circuit = Circuit(inputFileName)
    for line in inputFile:
        line = line.strip()
        if line.strip() != '':

            isInput = re.match('^INPUT', line)
            if isInput is not None:
                inputName = re.search('\([0-9A-Za-z]+\)', line)
                inputName = inputName.group(0)[1:-1]
                circuit.addInput(Cone(inputName))
                continue

            isOutput = re.match('^OUTPUT', line)
            if isOutput is not None:
                outputName = re.search('\([0-9A-Za-z]+\)', line)
                outputName = outputName.group(0)[1:-1]
                circuit.addOutput(Cone(outputName))
                continue

            isJump = re.match('^#', line)
            if isJump is not None:
                continue

            tokens = re.split('\W+', line)
            tokens = [x for x in tokens if x]
            if tokens[0] not in circuit.gates:
                circuit.addGates(Cone(tokens[0]))
            thisCone = circuit.getCone(tokens[0]);
            thisCone.operator = tokens[1];
            for token in tokens[2:]:
                thisCone.addInput(circuit.getCone(token))

    testVector = []
    if generateFiles is True:
        testFile.seek(0, 0)
        testFile.truncate()
        for input in circuit.inputs:
            value = random.randint(0,1)
            testVector.append(input.name+'='+str(value))
            circuit.gates[input.name].setOutput(value)
    else:
        testFile.seek(0, 0)
        for line in testFile:
            line = line.strip()
            if line.strip() != '':
                tokens = re.split('\W+', line)
                tokens = [x for x in tokens if x]
                circuit.gates[tokens[0]].setOutput(int(tokens[1]))
                testVector.append(tokens[0]+'='+str(int(tokens[1])))

    errorVector = []
    possible_errors = ['stuck-to-one', 'stuck-to-zero']
    if generateFiles is True:
        errorFile.seek(0, 0)
        errorFile.truncate()
        while len(errorVector) < math.floor((len(circuit.gates)-len(circuit.inputs))*errorRate/100): #fino a che gli errori non sono (massimo) ErrorRate delle porte totali
            index = random.randint(0, len(circuit.gates) - 1)
            rc = list(circuit.gates)[index]
            errorGate = circuit.getCone(rc)
            if len(errorGate.inputs) > 0 and errorGate.name not in errorVector:
                type_error = possible_errors[random.randint(0, len(possible_errors) - 1)]
                errorGate.setError(type_error)

                errorVector.append(errorGate.name+'='+type_error)
    else:
        errorFile.seek(0, 0)
        for line in errorFile:
            line = line.strip()
            if line.strip() != '':
                tokens = re.split('[^\w-]+', line)
                tokens = [x for x in tokens if x]
                circuit.gates[tokens[0]].setError(tokens[1])
                errorVector.append(tokens[0]+'='+tokens[1])

    circuit.updateValue()

    gates = list(circuit.gates)
    return

if __name__ == "__main__":
    main()