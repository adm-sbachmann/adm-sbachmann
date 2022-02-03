import os
from mutagen.flac import FLAC
import mysql.connector

sPath = '/srv/mk3/audiolane/mk3.album'
nCover, nFanart, nFolder, nFlac,nLengthAll = 0, 0, 0, 0, 0
lAlbumList = []

mydb = mysql.connector.connect(user='mk3dev', password='cherry',
                              host='127.0.0.1',
                              database='mk3dev')

mycursor = mydb.cursor()

for root, dirs, files in os.walk(sPath, topdown=True):

    dirs.sort()

    files.sort()

    for sName in files:
        if sName == 'cover.jpg':
            nCover += 1
        elif sName == 'fanart.jpg':
            nFanart += 1
        elif sName == 'folder.jpg':
            nFolder += 1
        else:
            nFlac += 1
            sPathFlac=(os.path.join(root, sName))
            pAudioinfo = FLAC(sPathFlac)

            try:
                sAudiodate = str(pAudioinfo['ORIGINALDATE'])[2:][:-2]
            except:
                sAudiodate = ''
            try:
                nAudioyear = int(str(pAudioinfo['ORIGINALYEAR'])[2:][:-2])
            except:
                nAudioyear = ''

            ## For songs

            sSongtitle = str(pAudioinfo['TITLE'])[2:][:-2]
            sSongtitle = sSongtitle.replace('"', '`')[:128]
            sSongreleasetrackID = str(pAudioinfo['MUSICBRAINZ_RELEASETRACKID'])[2:][:-2]
            nSongyear = nAudioyear;

            ## For albums

            sAlbum = str(pAudioinfo['ALBUM'])[2:][:-2]
            sAlbum = sAlbum.replace('"', '`')[:128]
            sAlbumreleasegroupID = str(pAudioinfo['MUSICBRAINZ_RELEASEGROUPID'])[2:][:-2]
            sAlbumartistID = str(pAudioinfo['MUSICBRAINZ_ALBUMARTISTID'])[2:][:-2]
            sAlbumartist = str(pAudioinfo['ALBUMARTIST'])[2:][:-2]
            sAlbumartistsort = str(pAudioinfo['ALBUMARTISTSORT'])[2:][:-2]
            nAlbumyear = nAudioyear
            sAlbumoriginaldate = sAudiodate

            print (sAlbumartist + " - " + sAlbum + " - " + sSongtitle + " - " + str(nSongyear))

            sSqlupdatealbum = 'REPLACE INTO collalbums (albumreleasegroupid, album, albumartistid,' \
                + ' albumartist, albumartistsort, albumyear, albumoriginaldate) VALUES ("' \
                + sAlbumreleasegroupID + '", "' + sAlbum + '", "' + sAlbumartistID + '", "' \
                + sAlbumartist + '", "' + sAlbumartistsort + '", "' + str(nAlbumyear) + '", "' \
                + sAlbumoriginaldate + '");'

            mycursor.execute(sSqlupdatealbum)
            mydb.commit()

            sSqlupdatesong = 'REPLACE INTO collsongs (songreleasetrackid, songtitle, filepath, albumreleasegroupid) VALUES ("' \
                + sSongreleasetrackID + '", "' + sSongtitle + '", "' + sPathFlac + '", "' + sAlbumreleasegroupID + '");'

            mycursor.execute(sSqlupdatesong)
            mydb.commit()

mydb.close()
