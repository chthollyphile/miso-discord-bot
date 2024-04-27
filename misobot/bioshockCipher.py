import sys

async def bioshockEnc(arg):
    # bioshockCipher输入范例: 
    #  P F V K Ar Mg Sc Al B Na Sc Ar Mn B
    #  w o u l d  y  o  u  k i  n  d  l  y

    key = 'suchong'
    mod = len(key)
    box = []
    count = 0
    cipherVg = ''
    plainText = ''
    elem = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe']
    opt = ''

    for i in key:
        num = ord(i) - ord('a')
        box.append(num)

    inputText = arg

    for i in inputText:
        if (ord('a') <= ord(i) and ord('z') >= ord(i)) or (ord('A') <= ord(i) and ord('Z') >= ord(i)):
            plainText += i
    plainText = plainText.lower()

    while count <= (len(plainText)-1):
        for i in range(mod):
            if count + i <= (len(plainText)-1):
                cipherVgText = chr((ord(plainText[count+i]) + box[i] - ord('a')) % 26 + ord('a'))
                cipherVg += cipherVgText
        count += mod

    for i in cipherVg:
        opt = opt +elem[ord(i)-ord('a')] + ' '

    return opt

async def bioshockDec(arg):
    # bioshockCipher输入范例: 
    #  P F V K Ar Mg Sc Al B Na Sc Ar Mn B
    #  w o u l d  y  o  u  k i  n  d  l  y

    key = 'suchong'
    mod = len(key)
    box = []
    count = 0
    cipherVgText = ''
    opt=''
    elem = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe']
    cipherVg = []

    for i in key:
        num = ord(i) - ord('a')
        box.append(num)

    inputText = arg
    inputList = inputText.split()
    mmFlag=False

    for i in inputList:
        for j in elem:
            if i == j:
                cipherVg.append(elem.index(j))
                mmFlag = True
        if mmFlag:
            mmFlag=False
        else:
            return f'只接受使用空格分隔开的bioshockCipher输入'
            # sys.exit()

    for item in cipherVg:
        letter = chr(item+ord('a'))
        cipherVgText+= letter

    while count <= (len(cipherVgText)-1):
        for i in range(mod):
            if count + i <= (len(cipherVgText)-1):
                plainText = chr((ord(cipherVgText[count+i]) - box[i] - ord('a')) % 26 + ord('a'))
                opt += plainText
        count += mod

    return opt

if __name__ == "__main__":
    bioshockEnc()
