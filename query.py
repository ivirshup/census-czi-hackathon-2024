import s3fs
import zarr
import dask.distributed as dd
from dask import delayed

from anndata.experimental import read_elem, read_elem_lazy
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix

import scipy.sparse as sp
import functools


class Census:

    def __init__(self, loc, n_workers=16):
        self.client = dd.Client(n_workers=n_workers)
        s3 = s3fs.S3FileSystem()
        self.stores = s3.ls(loc)

    @staticmethod
    def vstack_ptr(A, B):
        new_data = np.concatenate((A.data, B.data))
        new_indices = np.concatenate((A.indices, B.indices))
        new_ind_ptr = B.indptr + len(A.data)
        new_ind_ptr = new_ind_ptr[1:]
        new_ind_ptr = np.concatenate((A.indptr, new_ind_ptr))
        
        C = csr_matrix((new_data, new_indices, new_ind_ptr))
        return C


    def query_obs(self, key, val, cols):
        def _query_obs(store_uri, key, val, cols):
            df = pd.DataFrame()
        
            z = zarr.open(f"{store_uri}/obs/{key}/")
            data = read_elem(z)
            if np.any(data == val):
                df[key] = data
            else:
                return df
        
            cols.remove(key)
            
            for col in cols:
                z = zarr.open(f"{store_uri}/obs/{col}/")
                data = read_elem(z)
                df[col] = data
            df["dataset_id"] = store_uri.split("/")[-1]
            return df[df[key] == val]
        
        result = self.client.compute([delayed(_query_obs)(f"s3://{uri}", key, val, cols) for uri in self.stores])
        xs = self.client.gather(result)
        return pd.concat(xs, axis=0)
    

    def query_X(self, key, val):

        def _query_X(store_uri, key, val):
        
            z = zarr.open(f"{store_uri}/obs/{key}/")
            data = read_elem(z)
            idx = np.where(data == val)[0]
        
            z = zarr.open(f"{store_uri}/X/")
            W = read_elem_lazy(z)
        
            if not np.any(idx):
                return sp.csr_matrix((0, W.shape[1]))
        
            return W[idx, :].compute()
        
        result = self.client.compute([delayed(_query_X)(f"s3://{uri}", key, val) for uri in self.stores])
        xs = self.client.gather(result)
        return functools.reduce(lambda A, B: self.vstack_ptr(A, B), xs)