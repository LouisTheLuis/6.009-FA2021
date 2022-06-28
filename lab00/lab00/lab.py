# No Imports Allowed!


def backwards(sound):
    new_sound = {}
    new_sound['rate'] = sound['rate']
    
    temp_list1 = []
    for i in range(len(sound['left']) - 1, -1, -1):
        temp_list1.append(sound['left'][i])
    new_sound['left'] = temp_list1
    
    temp_list2 = []
    for i in range(len(sound['right']) -1 , -1, -1):
        temp_list2.append(sound['right'][i])
    new_sound['right'] = temp_list2
    
    return new_sound

def mix(sound1, sound2, p):

    if sound1['rate'] != sound2['rate']:
        return None
    
    elif p > 1 or p < 0:
        return None
    
    else:
        new_sound = {}
        new_sound['rate'] = sound1['rate']
        
        temp1_listLEFT = []
        temp2_listLEFT = []
        for i in range(len(sound1['left'])):
            temp1_listLEFT.append(sound1['left'][i]*p)
        for i in range(len(sound2['left'])):
            temp2_listLEFT.append(sound2['left'][i]*(1 - p))

        temp_LEFT = []
        if len(temp1_listLEFT) >= len(temp2_listLEFT):
            for i in range(len(temp2_listLEFT)):
                temp_LEFT.append(temp1_listLEFT[i] + temp2_listLEFT[i])
        else:
            for i in range(len(temp1_listLEFT)):
                temp_LEFT.append(temp1_listLEFT[i] + temp2_listLEFT[i])
        new_sound['left'] = temp_LEFT

        temp1_listRIGHT = []
        temp2_listRIGHT = []
        for i in range(len(sound1['right'])):
            temp1_listRIGHT.append(sound1['right'][i]*p)
        for i in range(len(sound2['right'])):
            temp2_listRIGHT.append(sound2['right'][i]*(1 - p))
        
        temp_RIGHT = []
        if len(temp1_listRIGHT) >= len(temp2_listRIGHT):
            for i in range(len(temp2_listRIGHT)):
                temp_RIGHT.append(temp1_listRIGHT[i] + temp2_listRIGHT[i])
        else:
            for i in range(len(temp1_listRIGHT)):
                temp_RIGHT.append(temp1_listRIGHT[i] + temp2_listRIGHT[i])
        new_sound['right'] = temp_RIGHT
        
        return new_sound

def echo(sound, num_echoes, delay, scale):
    new_sound = {}
    new_sound['rate'] = sound['rate']
    sample_delay = round(delay * sound['rate'])
    extra_length = (sample_delay * num_echoes)
    
    temp_listsLEFT = []
    for i in range(num_echoes + 1):
        temp_list = []
        for j in range(len(sound['left'])):
            temp_list.append(sound['left'][j] * (scale**i))
        temp_listsLEFT.append(temp_list)
    
    for i in range(len(temp_listsLEFT)):
        if i == 0:
            l = [0] * extra_length
            temp_listsLEFT[0].extend(l)

        else:
            l1 = [0] * sample_delay * i
            l3 = l1.copy()
            l2 = [0] * (extra_length - (sample_delay * i))
            l3.extend(temp_listsLEFT[i])
            l3.extend(l2)
            temp_listsLEFT[i] = l3.copy()
    
    leftlist = []
    for i in range(len(temp_listsLEFT[0])):
        value = 0
        for j in range(len(temp_listsLEFT)):
            value += temp_listsLEFT[j][i]
        leftlist.append(value)
        
    new_sound['left'] = leftlist
    
    temp_listsRIGHT = []
    for i in range(num_echoes + 1):
        temp_list = []
        for j in range(len(sound['right'])):
            temp_list.append(sound['right'][j] * (scale**i))
        temp_listsRIGHT.append(temp_list)
    
    for i in range(len(temp_listsRIGHT)):
        if i == 0:
            l = [0] * extra_length
            temp_listsRIGHT[0].extend(l)

        else:
            l1 = [0] * sample_delay * i
            l3 = l1.copy()
            l2 = [0] * (extra_length - (sample_delay * i))
            l3.extend(temp_listsRIGHT[i])
            l3.extend(l2)
            temp_listsRIGHT[i] = l3.copy()
    
    rightlist = []
    for i in range(len(temp_listsRIGHT[0])):
        value = 0
        for j in range(len(temp_listsRIGHT)):
            value += temp_listsRIGHT[j][i]
        rightlist.append(value)
        
    new_sound['right'] = rightlist   
            
    return new_sound

def pan(sound):
    new_sound = {}
    new_sound['rate'] = sound['rate']
    N = len(sound['left'])  #number of samples
    
    temp_listLEFT = []
    for i in range(len(sound['left'])):
        if i == 0:
            temp_listLEFT.append(sound['left'][0])
        elif i == len(sound['left']) - 1:
            temp_listLEFT.append(0)
        else:
            value = sound['left'][i] * (1 - (i / (N - 1)))
            temp_listLEFT.append(value)
    new_sound['left'] = temp_listLEFT
    
    
    temp_listRIGHT = []
    for i in range(len(sound['right'])):
        if i == 0:
            temp_listRIGHT.append(0)
        elif i == len(sound['left']) - 1:
            temp_listRIGHT.append(sound['right'][i])
        else:
            value = sound['right'][i] * (i / (N - 1))
            temp_listRIGHT.append(value)
    new_sound['right'] = temp_listRIGHT
    
    return new_sound


def remove_vocals(sound):
    new_sound = {}
    new_sound['rate'] = sound['rate']
    
    temp_list = []
    for i in range(len(sound['left'])):
        value = sound['left'][i] - sound['right'][i]
        temp_list.append(value)
    
    new_sound['left'] = temp_list
    new_sound['right'] = temp_list
    
    return new_sound


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
   hello = load_wav('sounds/hello.wav')
   damn = load_wav('mystery.wav')
   damn_2 = write_wav(backwards(damn), 'mystery2.wav')
    
   hola = load_wav('water.wav')
   hola2 = load_wav('synth.wav')
   hola3 = write_wav(mix(hola2, hola, 0.2), 'mix.wav')
    
   hey = load_wav('chord.wav')
   hey2 = write_wav(echo(hey, 5, 0.3, 0.6), 'new_chord.wav')
   write_wav(backwards(hello), 'hello_reversed.wav')
    
   bonjour = load_wav('car.wav')
   write_wav(pan(bonjour), 'car2.wav')
   
   ohayo = load_wav('lookout_mountain.wav')
   write_wav(remove_vocals(ohayo), 'lookout_mountain2.wav')