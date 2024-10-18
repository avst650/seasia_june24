import subprocess
 
command = 'CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir'
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, error = process.communicate()
output = output.decode("utf-8")
error = error.decode("utf-8")
print("Output:", output)
print("Error:", error)
 
command2 = 'pip install langchain'
print(command2)
process2 = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output2, error2 = process2.communicate()
output2 = output2.decode("utf-8")
error2 = error2.decode("utf-8")
print("Output:", output2)
print("Error:", error2)
