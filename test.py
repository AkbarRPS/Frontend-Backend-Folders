def hitung_total_harga(harga, jumlah):
    total_harga = harga * jumlah
    return total_harga

nama_barang = input("Masukkan nama barang: ")
harga_barang = float(input("Masukkan harga barang: "))
jumlah_barang = int(input("Masukkan jumlah barang: "))

total_harga = hitung_total_harga(harga_barang, jumlah_barang)
print("nama barang:", nama_barang)
print("harga barang:", harga_barang)
print("jumlah barang:", jumlah_barang)
print("total harga:", total_harga)

for i in range (5):
    print(i)
