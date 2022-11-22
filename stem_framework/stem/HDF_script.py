import zipfile
import h5py
import numpy as np


def zip_to_hdf(path_in, path_out, head_len=24, body_len=1024, name='name'):
    with zipfile.ZipFile(path_in) as file:
        streams = len(file.namelist())
        subfile_size = file.filelist[0].file_size
        starts_size = body_len * np.dtype('float32').itemsize
        starts = int(subfile_size / (starts_size + head_len))
        with h5py.File(path_out, 'w') as file_out:
            dataset = file_out.create_dataset(name, (starts, streams, body_len))
            for ind, filename in enumerate(file.namelist()):
                with file.open(filename) as subfile:
                    for i in range(starts):
                        subfile.seek(head_len, 1)
                        entry = np.frombuffer(subfile.read(starts_size))
                        dataset[i, ind, :] = entry
