import requests

# URL API yang diberikan
url = "http://192.168.114.137:9000/"

def post_data_to_api():
    try:
        # Mengirim permintaan POST ke URL tanpa payload
        response = requests.post(url)
        
        # Memeriksa apakah respons berhasil (status code 200)
        if response.status_code == 200:
            # Menguraikan data JSON dari respons
            data = response.json()
            
            # Mendapatkan nilai speed dan degree dari data JSON
            global_speed = data.get("speed")
            global_degree = data.get("degree")
            
            # Menampilkan hasil
            print(f"Speed: {global_speed}, Degree: {global_degree}")
        else:
            print(f"Gagal mendapatkan data dari API. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        # Menangani error jika terjadi kesalahan saat mengakses API
        print(f"Terjadi kesalahan saat mencoba mengakses API: {e}")

# Memanggil fungsi untuk mengirim permintaan POST ke API
post_data_to_api()
