from PIL import Image
import math
import random
import json
import base64
import requests
import shutil
import os

'''
TODO:
- Handle incorrect inputs
- Handle missing files
- Handle http request errors
- Compression
- Manage drive
'''

#Prompt for Upload / Download
print("Welcome to DesmosDrive!\n1. Upload\n2. Download")
ans = input("Enter number: ")

if ans == '1':
    #Uploading

    #Prepare binary
    fileName = input("Enter file name (with extension): ")
    print(f"Uploading from \'{fileName}\'!\nPreparing binary...")
    messageByte = open(fileName,'rb')
    data = messageByte.read()
    messageByte.close()
    data = ''.join(map(lambda x: '{:08b}'.format(x), data))
    data = data + (24-len(data)%24)*"0" #Fill with 0s to ensure full pixel data

    print("Uploading chunks...")
    hashes = []
    maxIMGbin = 24000000
    for hashN in range(math.ceil(len(data)/maxIMGbin)):
        #Convert binary to png
        colors = []
        limitL = hashN * maxIMGbin
        if hashN < math.floor(len(data)/maxIMGbin):
            limitR = limitL + maxIMGbin
        else:
            limitR = len(data)
        
        print(f"- Chunk {hashN+1}/{math.ceil(len(data)/maxIMGbin)} (Bit range: {limitL} - {limitR} out of {len(data)})")

        for i in range(int((limitR-limitL)/24)):
            red = int(data[limitL+24*i : limitL+24*i+8],2)
            green = int(data[limitL+24*i+8 : limitL+24*i+16],2)
            blue = int(data[limitL+24*i+16 : limitL+24*i+24],2)
            colors.extend([red,green,blue])

        #Save image to disk
        colors = bytes(colors)
        img = Image.frombytes('RGB', (int((limitR-limitL)/24), 1), colors)
        img.save("message.png")

        #Convert image to b64 and erase from disk (Is this necessary?)
        imgF = open("./message.png","rb")
        img64 = base64.b64encode(imgF.read())
        imgF.close()
        os.remove("message.png")

        #Generate graph hash (Is this done well enough?)
        hashN = bytes(int(10000000000 * random.random()))
        hashN = str(abs(hash(hashN)))[0:10]

        #Make POST request
        request = ''.join(["thumb_data=data%3Aimage%2Fpng%3Bbase64%2C", ascii(img64)[2:len(img64)+2],"&graph_hash=",str(hashN),"&my_graphs=false&is_update=false&calc_state={\"version\"%3A11%2C\"randomSeed\"%3A\"31204a3e2ef2c2d8289f2080bd62ba08\"%2C\"graph\"%3A{\"viewport\"%3A{\"xmin\"%3A-10%2C\"ymin\"%3A-4.4734251968503935%2C\"xmax\"%3A10%2C\"ymax\"%3A4.4734251968503935}}%2C\"expressions\"%3A{\"list\"%3A[{\"type\"%3A\"text\"%2C\"id\"%3A\"2\"%2C\"text\"%3A\"This graph contains a thumbnail encoded by DesmosDrive.\\n\\nBy%3A\\nDanielTheManiel\\nu%2FDanielTheManiel-\\ndanielthemaniel111\"}]}%2C\"includeFunctionParametersInRandomSeed\"%3Atrue}&lang=en&product=graphing"])
        request = request.replace("+","%2B").replace("/","%2F")
        headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-CA,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.desmos.com',
        'Priority': 'u=0',
        'Referer': 'https://desmos.com/calculator/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
        }
        response = requests.request("POST", "https://www.desmos.com/api/v1/calculator/save", headers=headers, data=request)

        hashes.append(hashN)

    #Save hash/filename to drive dictionary
    driveFile = open("drive.json", "r+")
    drive = json.loads(driveFile.read())
    drive[fileName] = hashes
    driveFile.seek(0)
    json.dump(drive, driveFile, indent = 4)
    driveFile.close()

    #Finish
    print("Saved!")

elif ans == '2':
    #Downloading

    #Prepare Drive
    driveFile = open("drive.json","r")
    drive = json.loads(driveFile.read())
    driveFile.close()
    print("---YOUR DRIVE---")
    for i in range(len(drive.keys())):
        print(f"{i+1}. {list(drive.keys())[i]}")
    
    #Prompt for file and get hash
    item = input("Enter file position: ")
    fileName = list(drive.keys())[int(item)-1]
    hashes = drive[fileName]

    print("Downloading...")
    chunk = 0
    message = []
    for hash in hashes:
        chunk = chunk + 1
        print(f"Chunk {chunk}/{len(hashes)}")
        #Fetch thumbnail and save to disk
        response = requests.get(f"https://www.desmos.com/calc_thumbs/production/{hash}.png", stream=True)
        with open('message.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        IMG = Image.open("message.png") #Again, is this necessary?
        pix = IMG.load()
        IMG.close()
        os.remove("message.png")

        #Read binary from image RGB
        for i in range(IMG.width):
            for j in pix[i,0]:
                message.append(j)
    
    #Write binary to file
    message = bytearray(message)
    newFile = open(fileName,"wb")
    newFile.write(bytes(message))
    newFile.close()
    
    #Finish
    print(f"{os.path.abspath(os.getcwd())}/{fileName}\nDownloaded!")