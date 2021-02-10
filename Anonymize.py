import datetime
import ner_anonymizer
import pyodbc
import sqlalchemy
import pandas as pd
import sys
import urllib

db_server = 'DB server name'
db_db = 'DB name'
db_username = 'DB username'
db_password = 'DB password'

f = open('Anonymize.out.txt', 'a')

conn_str = 'Driver={{SQL Server Native Client 11.0}};Server={};Database={};Uid={};Pwd={};'.format(db_server, db_db, db_username, db_password)
conn = pyodbc.connect(conn_str)

f.write(sys.argv[0])
if len(sys.argv) > 1:
    f.write(' {}'.format(sys.argv[1]))
    f.write(' {}'.format(sys.argv[2]))
f.write('\n')

message = '[{}] Phase 1 - Loading MyTable into memory, and running DataAnonymizer'.format(datetime.datetime.now())
print(message)
f.write(message)
f.write('\n')

sql = '''
    SELECT IdCol, Col002, Col003
    FROM MyTable WITH (NOLOCK)
    WHERE Col004 = 'Some condition'
'''

if len(sys.argv) > 1:
    sql = sql + 'AND IdCol >= {} '.format(sys.argv[1])
    sql = sql + 'AND IdCol <= {}'.format(sys.argv[2])

sql_query = pd.read_sql_query(sql, conn)
df = pd.DataFrame(sql_query, columns=['IdCol', 'Col002', 'Col003'])
anonymizer = ner_anonymizer.DataAnonymizer(df)
anonymized_df, _ = anonymizer.anonymize(
    free_text_columns=['Col003'],
    pretrained_model_name='dslim/bert-base-NER',
    label_list=['O', 'B-MISC', 'I-MISC', 'B-PER', 'I-PER', 'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC'],
    labels_to_anonymize=['B-PER', 'I-PER']
)

message = '[{}] Phase 2 - Replacing hashes with "XYZ"'.format(datetime.datetime.now())
print(message)
f.write(message)
f.write('\n')

anonymized_df['Col003'] = anonymized_df['Col003'].replace(
    to_replace=r'\b[a-z0-9]{32}\b',
    value='XYZ',
    regex=True
)

message = '[{}] Phase 3 - Inserting into MyTable_Anon'.format(datetime.datetime.now())
print(message)
f.write(message)
f.write('\n')

quoted = urllib.parse.quote_plus(conn_str)
engine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
anonymized_df.to_sql(
    name='MyTable_Anon',
    con=engine,
    schema='dbo',
    if_exists='append',
    index=False,
    chunksize=100,
    method='multi'
)

conn.close()

message = '[{}] End'.format(datetime.datetime.now())
print(message)
f.write(message)
f.write('\n')

f.close()
