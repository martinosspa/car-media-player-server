import socket
import time
import os

def main():
    HOST = ''  # The server's hostname or IP address
    PORT = 9999  # The port used by the server


    last_sync = str(time.time())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(last_sync.encode())
        print (1)
        data = s.recv(1024)
        #data = s.recv(1024)
        decoded_data = data.decode()

        print(decoded_data)
        if decoded_data == 'okay':
            # update last_sync to file
            return
        else:
            print(decoded_data)
            path = 'audio/'
            file_names = []
            print(1)
            for file_name in os.listdir(path):
                file_names.append(file_name)
                print(file_name)

            print(2)

            for file in file_names:
                s.send(file.encode())
                time.sleep(0.05)
                print(file)
            s.send('<END>'.encode())

            print(3)

            print(file_names)

            





        print('done')
    print('closed')

if __name__ == '__main__':
    main()