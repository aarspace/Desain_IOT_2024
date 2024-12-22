import asyncio
import cv2
import websockets

async def send_images():
    # Koneksi ke WebSocket server
    async with websockets.connect("ws://192.168.114.137:9999/sender") as websocket:
        # Membuka kamera (0 biasanya untuk kamera internal atau webcam USB pertama)
        cap = cv2.VideoCapture(1)

        # Cek apakah kamera berhasil dibuka
        if not cap.isOpened():
            print("Kamera tidak terdeteksi! Pastikan kamera USB terhubung.")
            return  # Keluar dari fungsi jika kamera tidak terdeteksi

        try:
            while True:
                # Membaca frame dari kamera
                ret, frame = cap.read()
                if not ret:
                    print("Tidak dapat membaca frame dari kamera!")
                    break

                # Encode frame sebagai JPEG
                buffer = cv2.imencode('.jpg', frame)[1].tobytes()

                # Mengirimkan data gambar (JPEG) ke server WebSocket
                await websocket.send(buffer)

                # Tunggu sedikit sebelum mengirim frame berikutnya (untuk mengontrol frame rate)
                await asyncio.sleep(0.05)  # Mengirim frame dengan interval sekitar 20 fps

        finally:
            # Pastikan kamera dilepas setelah streaming selesai
            cap.release()
            print("Kamera dilepas.")

# Jalankan fungsi send_images dengan asyncio event loop
asyncio.get_event_loop().run_until_complete(send_images())
