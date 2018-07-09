import os
from sys import path
#path.append('./snowboy-fly/examples/Python_voice/')
path.append('./Voice/')
import Voice_Sys
import voice_test
if __name__=='__main__':

    voice_t = voice_test.Voice()
    client_t = voice_t.client()
    # res = voice_t.run(client_t, "auto_detect.wav")
    # print res['result'][0]
    voice = Voice_Sys.Voice_Sys(voice_t,client_t)
    voice.run()