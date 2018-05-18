# Yandex.Audience python API

Python package wrapping APIs from https://tech.yandex.ru/audience/

## Installation

To install package, you can run:

```
git clone https://github.com/ssheremeta/yandex-audience-api.git
cd yandex-audience-api
pip install .
```

## Usage

Before using you must generate OAuth-token - https://tech.yandex.ru/oauth/doc/dg/tasks/get-oauth-token-docpage/


```
#Constants and Parameters
import hashlib
import cx_Oracle
import pandas as pd
import datetime
import yaaudience
    
# Constants, dont change 
c_ya_token = "<YANDEX_OAUTH_TOKEN>"
c_ora_connect_string = "<LOGIN>/<PASSWORD>@<TNS_NAME>"
c_data_filename = "/tmp/ya_data.csv"
c_clear_data_filename = "/tmp/clear_ya_data.csv"

# Parameters, CHANGE IT for your purpose
p_segment_name = 'mac_hashed_test1'

p_data_type = 'mac' # use one of {'phone', 'email', 'mac'}
p_data_hashed = True # use True of False

p_db_export_query = """ 
select mac_address from cusomers
"""

#Extracting data from DB
try:
    print('START')
    # Extract data from Database
    print("  start extracting data from DB")
    start = datetime.datetime.now()
    conn = None
    try:
        conn = cx_Oracle.connect(c_ora_connect_string, encoding = "UTF-8", nencoding = "UTF-8")
        df = pd.read_sql(p_db_export_query, con=conn)
        df.to_csv(c_data_filename, sep=',', header=False, index=False)    
    finally:
        if conn is not None:
            conn.close()
    exec_time = datetime.datetime.now() - start        
    print("    Elasped time: " + str(exec_time))
    print("  end extracting data from DB")

    # Clearing and hashing extracted data
    print("  start clearing/hashing data")    
    start = datetime.datetime.now()
    df = pd.read_csv(c_data_filename, header=None, dtype='str')
    df = df.applymap(lambda x: x.lower()) #transform entire dataframe to lowercase
    
    if p_data_type == 'phone':    
        df = df.replace('[^\d.]+', '',regex=True)
    elif p_data_type == 'mac':        
        df = df.replace('[;:,-\.]+', '',regex=True)    
        
    if p_data_hashed:
        if p_data_type != 'mac':
            df = df.applymap(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()) 
        else:
            df = df.applymap(lambda x: hashlib.md5(bytes.fromhex(x)).hexdigest()) 
            
    df.to_csv(c_clear_data_filename, sep=',', header=False, index=False)    
    print("    Elasped time: " + str(exec_time))
    print("  end clearing/hashing data")
    
except Exception as e:
    print('!!! Unexpected error: ' + str(e))
finally:
    print('FINISH')


#Sending data to Yandex.Audience
try:
    print('START')
    print("  start uploading segment data")
    start = datetime.datetime.now()
    ya = yaaudience.YaAudience(token=c_ya_token, debug=False)
    
    ya_segment_confirmed = None
    with open(c_clear_data_filename, 'r') as data_file:
        ya_segment_file_uploaded = ya.segments_upload_file(data_file)
        print(ya_segment_file_uploaded)
        
        ya_segment_confirmed = ya.segment_confirm(segment_id=ya_segment_file_uploaded.id, 
                                                  segment_name=p_segment_name, 
                                                  content_type=p_data_type, 
                                                  hashed=p_data_hashed)
        print(ya_segment_confirmed)
        
    exec_time = datetime.datetime.now() - start  
    print("    Elasped time: " + str(exec_time))
    print("  end uploading segment data")        
except Exception as e:
    print('!!! Unexpected error: ' + str(e))
finally:
    print('FINISH')

#View segments inside Yandex.Audience
try:
    print('START')
    print("  start receiving segments info")
    start = datetime.datetime.now()
    
    ya = yaaudience.YaAudience(token=c_ya_token)
    ya_segments = ya.segments()

    exec_time = datetime.datetime.now() - start          
    print("    Elasped time: " + str(exec_time))
    print("  end receiving segments info")        
    
    print("  Segments Count: ", ya_segments.__len__())            
    print("  Segments Details:")            
    for ya_segment in ya_segments:
        print(ya_segment)    
except Exception as e:
    print('!!! Unexpected error: ' + str(e))
finally:
    print('FINISH')

#Delete existing segment
segment_id_for_delete = '123456789'

try:
    print('START')
    print("  start deleting segment")
    start = datetime.datetime.now()

    if (segment_id_for_delete is None or segment_id_for_delete == ''):
        raise Exception('You mast set SEGMENT_ID for deleting!!!') 

    ya = yaaudience.YaAudience(token=c_ya_token)

    ya_is_segment_deleted = ya.segment_delete(segment_id=int(segment_id_for_delete))

    exec_time = datetime.datetime.now() - start          
    print("    Elasped time: " + str(exec_time))
    print("  end deleting segment")        
    
    print('  Is segment deleted? ' + str(ya_is_segment_deleted))    
except Exception as e:
    print('!!! Unexpected error: ' + str(e))
finally:
    print('FINISH')
```