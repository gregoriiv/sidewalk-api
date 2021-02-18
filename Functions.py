#Fuctions for Sidewalk API requests

# Function takes shapefile and returns coordinates of bbox
def Shp2Bbox(path):
    import shapefile as sf

    # getting shapefile
    shpf = sf.Reader(path)
    # check if shapefile contains POLYGON entities
    if shpf.shapeType == sf.POLYGON:
        # getting bbox
        shp_bb = shpf.bbox.tolist()
    else:
        print('Shapefile does not contain polygons. Please check up the shapefile.')
    
    return shp_bb

# Function makes request for given bbox and label_type
def AttributeRequest():
    import requests
    import json
    import yaml
    import os

    #create directory 'data' if not exists
    dir_main = 'data'
    if not os.path.exists(dir_main):
        os.mkdir(dir_main)

    #open config file and get variables
    with open('config_sidewalk.yaml') as m:
        config = yaml.safe_load(m)

    var = config['VARIABLES_SET']
    
    #get path, label_type, severity level
    path = var['path']
    labels = var['attributes']['label_types']
    severity_min = var['attributes']['severity_min']
    severity_max = var['attributes']['severity_max']

    bbox = Shp2Bbox(path)

    #assign coordinates from bbox
    lng1, lat1, lng2, lat2 = bbox[0], bbox[1], bbox[2], bbox[3]

    #create url for request
    url = ('https://sidewalk-spgg.cs.washington.edu/v2/access/attributes?lat1={}&lng1={}&lat2={}&lng2={}').format(lat1, lng1, lat2, lng2)

    # send the API request with no timeout
    r = requests.get(url,timeout=None)

    # if call fails, keeping trying until it succeeds with a 200 status code    
    while r.status_code != 200:
        r = requests.get(url,timeout=None)

    #form fespose in json format
    data = r.json()
    print('Total number of attributes in request: '+ str(len(data['features'])))
    
    #create json output
    output = {"type":"FeatureCollection","features":[]}

    for f in data['features']:
        if labels:
            if f['properties']['label_type'] in labels:
                if f['properties']['severity'] and f['properties']['severity'] >= severity_min and f['properties']['severity'] <= severity_max:
                    output['features'].append(f)
        else:
            if f['properties']['severity'] and f['properties']['severity'] >= severity_min and f['properties']['severity'] <= severity_max:
                output['features'].append(f)
    print('Number of attributes: ' + str(len(output['features'])))

    with open(os.path.join(dir_main,'attributes.geojson'), 'w') as outfile:
        print('Attributes file was written.')
        json.dump(output, outfile)

# Function for getting streets with scores
def SidewalkScoreRequest():
    import yaml
    import requests
    import json
    import os, sys

        
    #create directory 'data' if not exists
    dir_main = 'data'
    if not os.path.exists(dir_main):
        os.mkdir(dir_main)

    #open config file and get variables
    with open('config_sidewalk.yaml') as m:
        config = yaml.safe_load(m)

    var = config['VARIABLES_SET']
    
    #get path
    path = var['path']
    #get bbox from path
    bbox = Shp2Bbox(path)
    #get type of request neighborhoods or streets
    type_ = var['score_request']

    #assign coordinates from bbox
    lng1, lat1, lng2, lat2 = bbox[0], bbox[1], bbox[2], bbox[3]

    #create url for request
    url = ('https://sidewalk-spgg.cs.washington.edu/v2/access/score/{}?lat1={}&lng1={}&lat2={}&lng2={}').format(type_, lat1, lng1, lat2, lng2)

    # send the API request with no timeout
    r = requests.get(url,timeout=None)

    # if call fails, keeping trying until it succeeds with a 200 status code    
    while r.status_code != 200:
        r = requests.get(url,timeout=None)

    #form fespose in json format
    data = r.json()

    # print number of features
    print('Number of ' + type_ + ': ' + str(len(data['features'])))

    #create json output
    output = {"type":"FeatureCollection","features":[]}

    for f in data['features']:
        output['features'].append(f)

    #write down request resul in geojson file
    with open(os.path.join(dir_main,'score_' + type_ + '.geojson'), 'w') as outfile: 
        print(type_ + ' score file was written.')
        json.dump(output, outfile)
