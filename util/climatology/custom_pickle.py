import pickle

def save_to_pickle(data,savepath):

    with open(savepath, 'wb') as handle:

        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return None
 
def depickle(savepath):

    with open(savepath, 'rb') as handle:

        b = pickle.load(handle)

    return b
 