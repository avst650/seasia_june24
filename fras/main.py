import time
import subprocess
import signal
import os
import requests
import threading


def hit_django_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Successfully hit URL: {url}")
        else:
            print(f"Failed to hit URL: {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to hit URL: {url}. Error: {e}")



def start_runserver():
    # Replace the command with the command to start your Django server
    subprocess.Popen(["python", "manage.py", "runserver"])
    time.sleep(10)
    urls = ["http://127.0.0.1:8000/In_cam/", "http://127.0.0.1:8000/Out_cam/"]  # Replace with your Django project URLs
    threads = []
    for url in urls:
        thread = threading.Thread(target=hit_django_url, args=(url,))
        threads.append(thread)
        thread.start()
 
def stop_runserver():
    # Find and kill the Django runserver process
    output = subprocess.check_output(["ps", "aux"])
    for line in output.splitlines():
        if b"python manage.py runserver" in line:
            pid = int(line.split(None, 2)[1])
            os.kill(pid, signal.SIGKILL)

# def main():
#     print("Starting Django runserver...")
#     start_runserver()

#     try:
#         print("Waiting for 1 minute before restarting runserver...")
#         time.sleep(3600)  # 3600 seconds = 1 hrs
#         print("Restarting Django runserver...")
#         stop_runserver()
#         start_runserver()
#         print("Hitting Django project URL...")
#         time.sleep(10)
#         urls = ["http://127.0.0.1:8000/In_cam/", "http://127.0.0.1:8000/Out_cam/"]  # Replace with your Django project URLs
#         threads = []
#         for url in urls:
#             thread = threading.Thread(target=hit_django_url, args=(url,))
#             threads.append(thread)
#             thread.start()  # Replace with your Django project URL
#     except KeyboardInterrupt:
#         print("\nScript execution cancelled.")
 
# if __name__ == "__main__":
#     main()


def main():
    while True:
        print("Starting Django runserver...")
        start_runserver()
        try:
            print("Waiting for 1 hour before restarting runserver...")
            time.sleep(3600)  # Wait for 1 hour
            print("Restarting Django runserver...")
            stop_runserver()
            start_runserver()
            print("Hitting Django project URLs...")
            time.sleep(10)
            urls = ["http://127.0.0.1:8000/In_cam/", "http://127.0.0.1:8000/Out_cam/"]
            threads = []
            for url in urls:
                thread = threading.Thread(target=hit_django_url, args=(url,))
                threads.append(thread)
                thread.start()
            time.sleep(3600)
            stop_runserver()
        except KeyboardInterrupt:
            print("\nScript execution cancelled.")
            break  # Break out of the infinite loop on Ctrl+C
if __name__ == "__main__":
    main()