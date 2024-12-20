
import pandas as pd
import requests
import json
import numpy as np
from time import time

response = requests.get("https://dummyjson.com/products")

# mebaca dan merubah data dari json ke dalam dataframe 
data = response.json()
docs = data.get('products',[])
df = pd.DataFrame(docs)


# mengubah columns id menjadi id_product
df.rename(columns={'id': 'id_product'})

def memisahkan_column_dimension():
 # memisahkan column dimension
    df['width'] = df['dimensions'].apply(lambda x: x['width'])
    df['height'] = df['dimensions'].apply(lambda x: x['height'])

    df.drop(columns='dimensions', inplace=True)
    print('berhasil memisahkan column dimension')


def memisahkan_column_meta():    
# memisahkan column meta
    df['createdAt'] = df['meta'].apply(lambda x:x['createdAt'])
    df['updatedAt'] = df['meta'].apply(lambda x:x['updatedAt'])
    df['barcode'] = df['meta'].apply(lambda x:x['barcode'])
    df['qrCode'] = df['meta'].apply(lambda x:x['qrCode'])

    df.drop(columns='meta', inplace=True)

    print('berhasil memisahkan column meta')
    

def memisahkan_column_review():
     # memsihakan review dari tabel product
    product_review_df = df[['id', 'reviews']]

    df_exploded = product_review_df.explode('reviews')


    # Membuat DataFrame baru dari kolom 'reviews'
    df_reviews = pd.json_normalize(df_exploded['reviews'])

    # membuat column kosong baru
    df_reviews['id_product'] = None

    # perulangan untuk df review
    for index_df_review in range(len(df_reviews)):
        # perulangan untuk product review 
        for index_product_review_df in range(len(product_review_df)):
            # perulangan untuk setiap item pada product_review_df yang masih tergabung
            for index_rev_prod_id in range(len(product_review_df['reviews'][index_product_review_df])):
                # melakukan pengecekan jika pada reviews yang masih tergabung sama dengan review yang sudah dipisah
                # akan mengambil id jika datanya sama
                if df_reviews['reviewerName'][index_df_review] == product_review_df['reviews'][index_product_review_df][index_rev_prod_id]['reviewerName'] and \
                    df_reviews['comment'][index_df_review] == product_review_df['reviews'][index_product_review_df][index_rev_prod_id]['comment'] and \
                    df_reviews['date'][index_df_review] == product_review_df['reviews'][index_product_review_df][index_rev_prod_id]['date'] and \
                    df_reviews['rating'][index_df_review] == product_review_df['reviews'][index_product_review_df][index_rev_prod_id]['rating'] and \
                    df_reviews['reviewerEmail'][index_df_review] == product_review_df['reviews'][index_product_review_df][index_rev_prod_id]['reviewerEmail']:          
                    
                    df_reviews['id_product'][index_df_review] = product_review_df['id'][index_product_review_df]
                else:
                    False
    df.drop(columns='reviews', inplace=True)       

    print('berhasil memsihakan column reviews')

    return df_reviews
                    
nama_column = ['dimensions', 'meta']
# menjalankan pemisahan function pemisahan column
for column in nama_column:
    if column in df.columns:
        memisahkan_column_dimension()
        memisahkan_column_meta()
    else:
        print('nama column sudah dilakukan peisahan dan dihapus dalam df')

df_review = memisahkan_column_review()
df_product = df

# menambahkan id pada data review product
df_review['id_review'] = df_review.index + 1


# Mengonversi semua kolom bertipe numpy.int64 menjadi int
df_product = df_product.apply(lambda x: x.astype(int) if x.dtype == 'int64' else x)

df_product['id'] = df_product['id'].astype(int)

# koversi type data
# Dengan parameter tambahan
df_product = df_product.convert_dtypes(
    infer_objects=True,  # Coba inference tipe objek
    convert_string=True,  # Konversi ke string
    convert_integer=True,  # Konversi ke integer
    convert_floating=True  # Konversi ke floating point
)

df_review = df_review.convert_dtypes(
    infer_objects=True,  # Coba inference tipe objek
    convert_string=True,  # Konversi ke string
    convert_integer=True,  # Konversi ke integer
    convert_floating=True  # Konversi ke floating point
)


# Setelah convert_dtypes()
df_product = df_product.convert_dtypes()
df_review = df_review.convert_dtypes()

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from time import time
from sqlalchemy.types import Integer, String, Float, DateTime

def memuat_ke_postgres_3(df_product, df_review):

    # Buat engine koneksi
    engine = create_engine('postgresql://postgres:sikucing@localhost:5432/product_db')
    
    # Ukuran chunk
    chunk_size = 100

    try:
        # Pisahkan dataframe menjadi chunk
        df_iter_product = np.array_split(df_product, len(df_product) // chunk_size + (len(df_product) % chunk_size > 0))
        df_iter_review = np.array_split(df_review, len(df_review) // chunk_size + (len(df_review) % chunk_size > 0))
        
        for chunk_product, chunk_review in zip(df_iter_product, df_iter_review):
            # Waktu mulai
            t_start = time()
            
            # Untuk df product
            chunk_product.to_sql(
                name="product", 
                con=engine, 
                if_exists='append', 
                index=False,
                method='multi',
                chunksize=chunk_size
            )
            
            # Untuk df review product
            chunk_review.to_sql(
                name="review_product", 
                con=engine, 
                if_exists='append', 
                index=False,
                method='multi',
                chunksize=chunk_size
            )
            
            # Waktu berakhir
            t_end = time()
            print(f'Chunk berhasil ditambahkan, memerlukan waktu {t_end - t_start:.3f} detik')
    
    except Exception as e:
        print(f'Terjadi kesalahan: {e}')
        # Debugging: cetak tipe data
        print("\nTipe data Product:")
        print(df.dtypes)
        print("\nTipe data Review:")
        print(df_review.dtypes)
    
    finally:
        engine.dispose()

# menjalankan function memuat data ke dalam postgres
if __name__ == "__main__":
    memuat_ke_postgres_3(df_product, df_review)

