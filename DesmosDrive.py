from PIL import Image
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
'''

#Prompt for Upload / Download
print("Welcome to DesmosDrive!\n1. Upload\n2. Download")
ans = input("Enter number: ")

if ans == '1':
    #Uploading

    #Prepare binary
    fileName = input("Enter file name (with extension): ")
    print(f"Uploading from \'{fileName}\'...")
    messageByte = open(fileName,'rb')
    data = messageByte.read()
    messageByte.close()
    data = ''.join(map(lambda x: '{:08b}'.format(x), data))
    data = data + (24-len(data)%24)*"0" #Fill with 0s to ensure full pixel data

    #Convert binary to png
    colors = []
    for i in range(int(len(data)/24)):
        red = int(data[24*i : 24*i+8],2)
        green = int(data[24*i+8 : 24*i+16],2)
        blue = int(data[24*i+16 : 24*i+24],2)
        colors.extend([red,green,blue])

    #Save image to disk
    colors = bytes(colors)
    img = Image.frombytes('RGB', (int(len(data)/24), 1), colors)
    img.save("message.png")

    #Convert image to b64 and erase from disk (Is this necessary?)
    imgF = open("./message.png","rb").read()
    img64 = base64.b64encode(imgF)
    os.remove("message.png")

    #Generate graph hash (Is this done well enough?)
    hashN = 10000000000 * random.random()
    hashN = hash(hashN)
    hashN = hashN%10000000000 #Truncate to 10 digits

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
    'Sec-Fetch-Site': 'same-origin',
    'Cookie': 'AWSALB=pNfK7bLdwmhp6d3kzrnjBy50jJpFlRq4a+J2n4+NEPchQI1+qvwvuV+YSOeJv2LdlDi+yoLVsdB6wB07Hqz2Gr3D92htrqnbx+3Ht398uJCsfX/s+vHaZ/PZDF1Q; AWSALBCORS=pNfK7bLdwmhp6d3kzrnjBy50jJpFlRq4a+J2n4+NEPchQI1+qvwvuV+YSOeJv2LdlDi+yoLVsdB6wB07Hqz2Gr3D92htrqnbx+3Ht398uJCsfX/s+vHaZ/PZDF1Q'
    }
    response = requests.request("POST", "https://www.desmos.com/api/v1/calculator/save", headers=headers, data=request)

    #Save hash/filename to drive dictionary
    driveFile = open("drive.json", "r+")
    drive = json.loads(driveFile.read())
    drive[fileName] = hashN
    driveFile.seek(0)
    json.dump(drive, driveFile, indent = 4)
    driveFile.close()

    #Finish
    print(f"https://www.desmos.com/calc_thumbs/production/{hashN}.png\nSaved!")

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
    hash = drive[fileName]

    #Fetch thumbnail and save to disk
    response = requests.get(f"https://www.desmos.com/calc_thumbs/production/{hash}.png", stream=True)
    with open('message.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    IMG = Image.open("message.png") #Again, is this necessary?
    pix = IMG.load()
    os.remove("message.png")

    #Read binary from image RGB
    message = []
    for i in range(IMG.width):
        for j in pix[i,0]:
            message.append(j)
    message = bytearray(message)
    
    #Write binary to file
    newFile = open(fileName,"wb")
    newFile.write(bytes(message))
    newFile.close()
    
    #Finish
    print(f"{os.path.abspath(os.getcwd())}/{fileName}\nDownloaded!")