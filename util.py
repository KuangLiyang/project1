from ftplib import FTP
import os
import cognitive_face as CF
class FTP_Uploader(object):
  def __init__(self):
    self.server_ip = "144.202.109.208"
    self.user_name = "ftpuser"
    self.user_passwd = "ldavid989"
    self.ftp = self.ftpconnect(self.server_ip, self.user_name, self.user_passwd)
    self.remote_home_path = self.ftp.pwd()


  def run(self, imgName):
    _, remote_file_name = os.path.split(imgName)
    print remote_file_name
    upload_path = os.path.join(self.remote_home_path, "www", remote_file_name)
    print upload_path
    self.uploadfile(self.ftp, upload_path, imgName)

  def uploadfile(self, ftp, remotepath, localpath):
    bufsize = 10240
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

  def ftpconnect(self, host, username, password):
    ftp = FTP()
    ftp.connect(host, 21)
    ftp.login(username, password)
    return ftp

class Face_Detect():
  def __init__(self):
    #self.KEY = 'fbe56bfa514b4f53a35541f56bdccd85'  # Replace with a valid Subscription Key here.
    self.KEY='3b794b9d493c40c99f906335e1a2e53f'
    CF.Key.set(self.KEY)

    self.BASE_URL = 'https://eastasia.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL
    CF.BaseUrl.set(self.BASE_URL)

  def run(self, imgName):
    _, remote_imgName = os.path.split(imgName)
    #img_url = 'http://144.202.109.208/%s' % remote_imgName
    #print img_url
    #result = CF.face.detect(img_url, face_id=True, landmarks=False, attributes="age,gender")
    result=CF.face.detect(imgName,  attributes="gender,age")
    return result

if __name__ == "__main__":
  imgName = "./2.jpg"
  img_uploader = FTP_Uploader()
  img_uploader.run(imgName)

  face = Face_Detect()
  result = face.run(imgName)
  print result