#-------------------------------------------------------------------------
# AUTHOR: Lauren Contreras
# FILENAME: db_connection_solution.py
# SPECIFICATION: This program is meant to use the corpus databse to manage an inverted index.
#                It connect to the database, creates categories and documents, deletes documents,
#                updates document, and gets the inverted index.
# FOR: CS 4250- Assignment #2
# TIME SPENT: 3 hours
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
# --> add your Python code here
import psycopg2
from psycopg2.extras import RealDictCursor
from string import punctuation
def connectDataBase():
    DB_NAME = "corpus"
    DB_USER = "postgres"
    DB_PASS = "123"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    try:
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT,
                                cursor_factory=RealDictCursor)
        return conn

    except:
        print("Database not connected successfully")
    # Create a database connection object using psycopg2
    # --> add your Python code here

def createCategory(cur, catId, catName):

    # Insert a category in the database
    # --> add your Python code here
    sql = 'INSERT into "public"."Categories" (id_cat, name) VALUES (%s, %s)'
    recset = [catId, catName]
    cur.execute(sql, recset)
def createDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Get the category id based on the informed category name
    # --> add your Python code here
    sql = 'SELECT id_cat FROM "public"."Categories" WHERE name = %s'
    recset = [docCat,]
    cur.execute(sql, recset)
    row = cur.fetchone()
    
    if row is not None:
        catId = row['id_cat']
    else:
        raise Exception("Error", docCat)
    
    # 2 Insert the document in the database. For num_chars, discard the spaces and punctuation marks.
    # --> add your Python code here
    num_chars = len(docText.replace(" ", " ").translate(str.maketrans('','', punctuation)))
    sql = 'INSERT INTO "public"."Documents" (doc, text, title, num_chars, date, cat_id) VALUES (%s, %s, %s, %s, %s, %s)'
    recset = [docId, docText, docTitle, num_chars, docDate, catId]
    cur.execute(sql, recset)
    
    # 3 Update the potential new terms.
    # 3.1 Find all terms that belong to the document. Use space " " as the delimiter character for terms and Remember to lowercase terms and remove punctuation marks.
    # 3.2 For each term identified, check if the term already exists in the database
    # 3.3 In case the term does not exist, insert it into the database
    # --> add your Python code here
    terms = set(docText.lower().split())
    for term in terms:
        sql = 'INSERT INTO "public"."Terms" (term, num_chars) VALUES (%s,%s) ON CONFLICT DO NOTHING'
        recset = [term.translate(str.maketrans('','', punctuation)), len(term)]
        cur.execute(sql, recset)
    # 4 Update the index
    # 4.1 Find all terms that belong to the document
    # 4.2 Create a data structure the stores how many times (count) each term appears in the document
    # 4.3 Insert the term and its corresponding count into the database
    # --> add your Python code here
    for term in terms:
        term_count = docText.lower().split().count(term)
        sql = 'INSERT INTO "public"."Doc_Terms" (doc_number, term_t, term_count) VALUES (%s, %s, %s) ON CONFLICT (doc_number, term_t) DO UPDATE SET term_count = "public"."Doc_Terms".term_count + %s'
        recset = [docId, term.translate(str.maketrans('','', punctuation)), term_count, term_count]
        cur.execute(sql, recset)
def deleteDocument(cur, docId):

    # 1 Query the index based on the document to identify terms
    # 1.1 For each term identified, delete its occurrences in the index for that document
    # 1.2 Check if there are no more occurrences of the term in another document. If this happens, delete the term from the database.
    # --> add your Python code here
    sql = 'SELECT term_t FROM "public"."Doc_Terms" WHERE doc_number = %s'
    recset = [docId,]
    cur.execute(sql, recset)
    terms = cur.fetchall()

    for term in terms:
        term_t = term['term_t']
        sql = 'DELETE FROM "public"."Doc_Terms" WHERE doc_number = %s AND term_t = %s'
        recset = [docId,term_t]
        cur.execute(sql, recset)
        
        sql = 'SELECT COUNT(*) FROM "public"."Doc_Terms" WHERE term_t = %s'
        recset = [term_t,]
        cur.execute(sql, recset)
        count_row = cur.fetchone()
        
        if count_row is not None:
            count = count_row['count']
            if count == 0:
                sql = 'DELETE FROM "public"."Terms" WHERE term = %s'
                recset = [term_t,]
                cur.execute(sql, recset)
        
    sql = 'DELETE FROM "public"."Documents" WHERE doc = %s'
    recset = [docId,]
    cur.execute(sql, recset)
    # 2 Delete the document from the database
    # --> add your Python code here

def updateDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Delete the document
    # --> add your Python code here
    deleteDocument(cur, docId)
    # 2 Create the document with the same id
    # --> add your Python code here
    createDocument(cur, docId, docText, docTitle, docDate, docCat)
def getIndex(cur):

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    # --> add your Python code here
    index = {}
    sql = 'SELECT d.title, dt.term_t, dt.term_count FROM "public"."Doc_Terms" dt JOIN "public"."Documents" d ON dt.doc_number = d.doc'
    recset = [sql,]
    cur.execute(sql,recset)
    rows = cur.fetchall()
    for row in rows:
        title = row['title']
        term = row['term_t']
        term_count = row['term_count']

        if term in index:
            index[term] += f",{title}:{term_count}"
        else:
            index[term] = f"{title}:{term_count}"

    index = dict(sorted(index.items()))
    
    return index
   
