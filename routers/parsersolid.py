import requests
import json
import csv

# consts
url_1='https://rest.isric.org/soilgrids/v2.0/properties/query?'
url_2='&property=ocd&property=ocs&property=bdod&property=clay&property=cfvo&property=sand&property=silt&&property=cec&property=nitrogen&property=phh2o&property=soc&value=mean'

names = ["Bulk density", "Cation exchange capacity (at ph 7)", "Coarse fragments", "Clay content", "nitrogen", "Organic carbon density", "Soil organic carbon stock", "pH water", "Sand", "Silt", "Soil organic carbon"]
csvfile = open("final.csv", "w")

def get_json(lon, lat):
    data = requests.get(f'{url_1}lon={lon}&lat={lat}{url_2}')
    return(data.content)


def get_beautifull(lon, lat):
    finalarr = []
    data = json.loads(get_json(lon, lat))
    len_layers = len(data['properties']['layers'])
    
    # print(data['properties']['layers'][0]['name'])
    for i in range(len_layers):
        arr = []
        # print(data['properties']['layers'][i]['name'])
        len_depths = len(data['properties']['layers'][i]['depths'])
        for j in range(len_depths):
            arr.append(data['properties']['layers'][i]['depths'][j]['values']['mean'])
        ans = {names[i]:arr}
        finalarr.append(ans)
    if arr[0]:
        return finalarr
    else:
        return [119, 308, 102, 290, 490, 339]
        

# csvwriter = csv.writer(csvfile)
# csvwriter.writerow(names)
# for i in range (50): #45-50; 46-80
#     csvfile = open("final.csv", "w")
#     for j in range (100):
#         get_beautifull(lon=45+i/10, lat=46 + j*0.34)
#     csvfile.close()
# csvfile.close()
# get_beautifull(lon=84.989147952404, lat=53.15010248274143)
