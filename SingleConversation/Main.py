import mysql.connector    
import json
from datetime import datetime

#Global Vars
cnx = mysql.connector.connect(user='DarrinS', password='dsuserpw', host='192.168.1.193', database='ShittyChat')
cursor = cnx.cursor()
dataLoc = "D:\\"
mediaTypes = {} #Gets populated with the media types in the table on start up.  Table needs to be filled before script runs.

def AddMedia(type, jsonObj, messageID):
    for media in jsonObj:
        with open(dataLoc + media["uri"], 'rb') as f:
            sql = ("""
            INSERT INTO Media 
                (MessageID, MediaTypeID, FileName, FileContent) 
            VALUES 
                (%(MessageID)s, %(MediaTypeID)s, %(FileName)s, %(FileContent)s)""")
            params = {"MessageID" : messageID,
                      "MediaTypeID" : mediaTypes[type],
                      "FileName" : media["uri"].rsplit('/', 1)[-1],
                      "FileContent" : f.read()}
            cursor.execute(sql, params)
            cnx.commit()

            #If the media being stored is a video, it should(?) have a thumbnail associated with it.
            if type == "videos" and "thumbnail" in media:
                with open(dataLoc + media["thumbnail"]["uri"], 'rb') as tn:
                    sql = ("""
                    INSERT INTO Media 
                        (MessageID, MediaTypeID, FileName, FileContent) 
                    VALUES 
                        (%(MessageID)s, %(MediaTypeID)s, %(FileName)s, %(FileContent)s)""")
                    params = {"MessageID" : messageID,
                            "MediaTypeID" : mediaTypes["thumbnail"],
                            "FileName" : media["thumbnail"]["uri"].rsplit('/', 1)[-1],
                            "FileContent" : tn.read()}
                    cursor.execute(sql, params)
                    cnx.commit()


def main():
    jsonData = []
    with open(f"{dataLoc}\\messages\\ThisPlaceWishesItWasShenanigans_e72a84c1a1\\message.json") as f:
        jsonData = json.load(f)

    #Clear all tables before running.
    sql = ("TRUNCATE TABLE Participant")
    cursor.execute(sql)
    sql = ("TRUNCATE TABLE Message")
    cursor.execute(sql)
    sql = ("TRUNCATE TABLE Reaction")
    cursor.execute(sql)
    sql = ("TRUNCATE TABLE Media")
    cursor.execute(sql)
    sql = ("TRUNCATE TABLE Share")
    cursor.execute(sql)
    sql = ("TRUNCATE TABLE Plan")
    cursor.execute(sql)
    sql = ("TRUNCATE TABLE User")
    cursor.execute(sql)
    sql = ("TRUNCATE TABLE PaymentInfo")
    cursor.execute(sql)

    #Populate the mediaTypes dict.
    sql = ("SELECT * FROM MediaType")
    cursor.execute(sql)
    result = cursor.fetchall()
    for type in result:
        mediaTypes[type[1]] = type[0]

    #Add all the participants for this conversation.
    myPpl = { } #Dictionary of people so we don't have to ask the DB everytime.
    for person in jsonData['participants']:
        sql = ("""
        INSERT INTO Participant 
            (Name) 
        VALUES 
            (%(Name)s)""")
        params = {'Name' : person['name']}
        cursor.execute(sql, params)
        cnx.commit()
        myPpl[person['name']] = cursor.lastrowid

    #Loop through all the messages in the conversation.
    for i, message in enumerate(jsonData['messages']):
        if i % 100 == 0:
            print(f"{i} done out of {len(jsonData['messages'])}")

        # Checks for if message was sent by someone not in group (they were once part of the group but left).
        if message["sender_name"] not in myPpl:
            sql = ("""
            INSERT INTO Participant 
                (Name) 
            VALUES 
                (%(Name)s)""")
            params = {'Name' : message["sender_name"]}
            cursor.execute(sql, params)
            cnx.commit()
            myPpl[message["sender_name"]] = cursor.lastrowid

        # Insert the message and save the ID it was given.
        sql = ("""
        INSERT INTO Message 
            (SenderID, Timestamp, Type, Content) 
        VALUES 
            (%(SenderID)s, %(Timestamp)s, %(Type)s, %(Content)s)""")
        params = {"SenderID" : myPpl[message["sender_name"]],
                  "Timestamp" : datetime.utcfromtimestamp(message["timestamp_ms"]/1000).strftime("%Y-%m-%d %H:%M:%S"), #FB reports in Unix time to the ms.
                  "Type" : message["type"],
                  "Content" : message["content"] if "content" in message else None}
        cursor.execute(sql, params)
        cnx.commit()
        messageID = cursor.lastrowid

        # Insert the reactions the message had.
        if "reactions" in message:
            for reaction in message["reactions"]:
                sql = ("""
                INSERT INTO Reaction 
                    (MessageID, Actor, Reaction) 
                VALUES 
                    (%(MessageID)s, %(Actor)s, %(Reaction)s)""")
                params = {"MessageID" : messageID,
                          "Actor" : myPpl[reaction["actor"]], 
                          "Reaction" : reaction["reaction"]}
                cursor.execute(sql, params)
                cnx.commit()

        try:
            # Determine what kind of message it was.
            if "photos" in message:
                AddMedia("photos", message["photos"], messageID)
            elif "gifs" in message:
                AddMedia("gifs", message["gifs"], messageID)
            elif "videos" in message:
                AddMedia("videos", message["videos"], messageID)
            elif "files" in message:
                AddMedia("files", message["files"], messageID)
            elif "audio_files" in message:
                AddMedia("audio_files", message["audio_files"], messageID)
            elif "share" in message:
                sql = ("""
                INSERT INTO Share 
                    (MessageID, Link, Text) 
                VALUES 
                    (%(MessageID)s, %(Link)s, %(Text)s)""")
                params = {"MessageID" : messageID,
                          "Link" : message["share"]["link"] if "link" in message["share"] else None, # Some Share's don't have a "link".
                          "Text" : message["share"]["share_text"] if "share_text" in message["share"] else None}# Some Share's don't have a "share_text".
                cursor.execute(sql, params)
                cnx.commit()
                # messageID = cursor.lastrowid
            elif "sticker" in message:
                with open(dataLoc + message["sticker"]["uri"], 'rb') as stickerContent:
                    sql = ("""
                    INSERT INTO Media 
                        (MessageID, MediaTypeID, FileName, FileContent) 
                    VALUES 
                        (%(MessageID)s, %(MediaTypeID)s, %(FileName)s, %(FileContent)s)""")
                    params = {"MessageID" : messageID,
                            "MediaTypeID" : mediaTypes["sticker"],
                            "FileName" : message["sticker"]["uri"].rsplit('/', 1)[-1],
                            "FileContent" : stickerContent.read()}
                    cursor.execute(sql, params)
                    cnx.commit()
            elif "plan" in message:
                sql = ("""
                INSERT INTO Plan 
                    (MessageID, Title, Timestamp, Location) 
                VALUES 
                    (%(MessageID)s, %(Title)s, %(Timestamp)s, %(Location)s)""")
                params = {"MessageID" : messageID,
                          "Title" : message["plan"]["title"] if "title" in message["plan"] else None, # Some Plan's don't have a "title".
                          "Timestamp" : datetime.utcfromtimestamp(message["plan"]["timestamp"]/1000).strftime("%Y-%m-%d %H:%M:%S"),
                          "Location" : message["plan"]["location"] if "location" in message["plan"] else None} #FB Some Plan's don't have a "location".
                cursor.execute(sql, params)
                cnx.commit()
            elif "users" in message:
                for user in message["users"]: # Users is an array, so possibility for more than one but haven't seen this yet.
                    sql = ("""
                    INSERT INTO User 
                        (MessageID, Name) 
                    VALUES 
                        (%(MessageID)s, %(Name)s)""")
                    params = {"MessageID" : messageID,
                              "Name" : user["name"]}
                    cursor.execute(sql, params)
                    cnx.commit()
            elif "payment_info" in message:
                sql = ("""
                INSERT INTO PaymentInfo
                    (MessageID, Amount, Currency, CreationTime, CompletedTime, SenderID, ReceiverID) 
                VALUES 
                    (%(MessageID)s, %(Amount)s, %(Currency)s, %(CreationTime)s, %(CompletedTime)s, %(SenderID)s, %(ReceiverID)s)""")
                params = {"MessageID" : messageID,
                          "Amount" : message["payment_info"]["amount"],
                          "Currency" : message["payment_info"]["currency"],
                          "CreationTime" : datetime.utcfromtimestamp(message["payment_info"]["creationTime"]/1000).strftime("%Y-%m-%d %H:%M:%S"),
                          "CompletedTime" : datetime.utcfromtimestamp(message["payment_info"]["completedTime"]/1000).strftime("%Y-%m-%d %H:%M:%S") if "completedTime" in message["payment_info"] else None,
                          "SenderID" : myPpl[message["payment_info"]["senderName"]],
                          "ReceiverID" : myPpl[message["payment_info"]["receiverName"]]}
                cursor.execute(sql, params)
                cnx.commit()
        except Exception as e:
            print(message["timestamp_ms"])
            print(e)
            return
        
    print("Hello World!")

if __name__ == "__main__":
    main()