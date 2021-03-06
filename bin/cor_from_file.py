__author__ = 'Anders'
import sys
import numpy as np


def read_file(filename=None):
    '''
    Read in Becker&Hickl SPC files
    :param filename: path to file to be read
    :return: Macrotime, Channel, SyncRate
    '''
    data = np.fromfile(filename, dtype='uint32')
    SyncRate = np.bitwise_and(data[0], 16777215)
    data = np.delete(data, 0)
    rout = np.bitwise_and((data >> 8), 240)
    rout = np.uint8(rout)
    mark = np.bitwise_and((data >> 28), 15)
    mark = np.uint8(mark)
    #mark = mark + rout

    MT = np.zeros(mark.size, np.uint32)
    MT[np.bitwise_and(mark, 12) == 4] = 1
    MT[np.bitwise_and(mark, 12) == 12] = np.bitwise_and(data[np.bitwise_and(mark, 12) == 12], 268435455)

    Macrotime = np.uint16(np.bitwise_and(data, 4095))
    MI = 4095 - np.uint16(np.bitwise_and((data >> 16), 4095))
    MT = np.cumsum(np.double(MT)) * 4096 + np.double(Macrotime)
    MT = MT.astype(int)

    invalid = (np.bitwise_and(mark, 8) == 8)
    MI = MI[~invalid]
    MT = MT[~invalid]
    mark = mark[~invalid]
    rout = rout[~invalid]
    SyncRate = 1E10 / np.double(SyncRate)

    return MT, (rout/16).astype(int), SyncRate

def save_corr(data,filename):
    '''Impement save to .txt file'''
    if filename is None:
        filename = "test.cor"
    txt_name = filename[:len(filename)-3]+'cor'
    with open(txt_name, 'w') as f: # open filename
        f.write('Correlation file for: '+filename+'\n')
        f.write('Countrate channel 1 [kHz]: '+str(0)+'\n')
        f.write('Countrate channel 2 [kHz]: '+str(0)+'\n')
        f.write('Valid bins: '+str(np.ones(10))+'\n')
        f.write('Data starts here: \n')
        np.savetxt(f, data)
        f.close()


def main(filename=None):
    import multipletau_cor_tttr
    import time
    if filename is None:
        filename = 'sampledata/sample.spc'
    mt, chan, sync = read_file(filename)
    start = time.time()
    c, ec, t = multipletau_cor_tttr.correlate.CCF(mt.astype(float).tolist(), mt.astype(float))
    stop = time.time()
    print(stop-start)
    np.save("sampledata/sample_data",mt)
    data = np.transpose(np.vstack((t/sync,c,ec))) # arrange in correct manner for text file
    data = np.hstack((data,np.zeros((data.shape[0],10))))
    save_corr(data, filename)

    from matplotlib import pyplot as plt
    plt.errorbar(t/sync, c, ec)
    plt.xscale('log')
    plt.xlabel('Timelag t (s)')
    plt.ylabel('G(t)')
    plt.xlim((1e-6, 1))
    plt.ylim((np.min(c-ec),np.max(c+ec)))
    plt.axvline(5E-4,linestyle='-')
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        main(sys.argv[1])
