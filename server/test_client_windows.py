import socket
import time
import os

def main():
    HOST = '66.205.82.239'  # The server's hostname or IP address
    PORT = 9999  # The port used by the server


    last_sync = str(time.time())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(last_sync.encode())
        print (1)
        for _ in range(100):
            data = s.recv(1024)
        decoded_data = data.decode()
        
        if decoded_data == 'okay':
            # update last_sync to file
            return
        print(decoded_data)
        path = os.getcwd() + '\\Desktop\\audio'
        file_names = []
        print (1)
        for file_name in os.listdir(path):
            #audio_file_name = os.path.join(path, file_name)
            file_names.append(file_name)
            print(file_name)

        print (2)

        for file in file_names:
            s.send(file.encode())
            time.sleep(0.05)
            print(file)
        s.send('<END>'.encode())

        
        print (2)

        print(file_names)

        






    print(f'closed')

if __name__ == '__main__':
    main()