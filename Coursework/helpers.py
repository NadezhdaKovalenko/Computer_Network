import numpy as np
import multiprocessing as mp
import ctypes

def get_x(vec):
    return vec[0]


def get_y(vec):
    return vec[1]


def normalize(vec):
    return vec / np.linalg.norm(vec)


def real_attr(obj, attr):
    return object.__getattribute__(obj, attr)


def make_shared_arr(size=2):
    return mp.Array(ctypes.c_double, size)


def modify_shared_arr(callback, shared_arr):
    with shared_arr.get_lock(): # synchronize access
        arr = np.frombuffer(shared_arr.get_obj()) # no data copying
        return callback(arr)
    

def array_from_shared(shared_arr):
    with shared_arr.get_lock():
        arr = np.frombuffer(shared_arr.get_obj())
        return arr.copy()
    
    
def shared_from_array(arr):
    """
    Works with one-dimensional data only
    """
    shared_arr = make_shared_arr(len(arr))
    with shared_arr.get_lock(): # synchronize access
        new_arr = np.frombuffer(shared_arr.get_obj()) # no data copying
        new_arr[:] = arr[:]
    return shared_arr


def shared_from_double(val):
    return mp.Value(ctypes.c_double, val)


def double_from_shared(shared_val):
    with shared_val.get_lock():
        return shared_val.value


FOCUS_HEIGHT = 5.0
LIGHT_HEIGHT = 10.0
WIDTH = 1.0

ANGLE_LIMIT = np.pi / 8


def random_pos(kind='mirror'):
    pos = np.random.rand(2)
    if kind == 'mirror':
        pos *= 5.0
        pos -= 2.5
    elif kind == 'focus':
        pos[1] += FOCUS_HEIGHT
    elif kind == 'light':
        pos[1] += LIGHT_HEIGHT
    else:
        raise Exception(f"Incorrect kind: {kind}")
    return pos
        

def random_vel():
    res = np.random.rand(2) / 1000.0
    res[1] = 0.0
    return res


def random_width():
    return np.random.rand() + WIDTH


def random_angle():
    return np.pi / 2 - np.random.rand() * ANGLE_LIMIT


def reflect_vector(point, normal):
    projection = np.dot(point, normal)
    return point - 2 * projection * normal


def cross(normal):
    return np.array([-normal[1], normal[0]])