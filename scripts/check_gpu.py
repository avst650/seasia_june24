import tensorflow.python.platform.build_info as build
import tensorflow as tf
import subprocess

print("\nNum GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
print(tf.config.list_physical_devices('GPU'))
print('cuda:', build.build_info['cuda_version'])
print('cudnn:', build.build_info['cudnn_version'])
subprocess.Popen('dpkg-query -W tensorrt', shell=True)
