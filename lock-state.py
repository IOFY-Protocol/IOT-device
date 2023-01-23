import pickle


def lock_state():
    # An arbitrary collection of objects supported by pickle.
    locked = True
    with open('locked.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(locked, f, pickle.HIGHEST_PROTOCOL)


def unlock_state():
    # An arbitrary collection of objects supported by pickle.
    locked = False
    with open('locked.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(locked, f, pickle.HIGHEST_PROTOCOL)


def read_state():
    with open('locked.pickle', 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        data = pickle.load(f)
    print(data)
    return data
