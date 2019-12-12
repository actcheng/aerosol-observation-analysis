
def extract_tar(tarname,path=None):
  import tarfile
  import os

  tar = tarfile.open(tarname)

  if not path:
    path = os.getcwd()

  print('Extracting tar file: {} at {}'.format(tarname,path))
  tar.extractall(path=path)
  tar.close()
  print('Finish extracting tar file')
  return

def draw_progress_bar(percent, bar_len = 50):
  import sys
  sys.stdout.write("\r")
  progress = ""
  for i in range(bar_len):
      if i < int(bar_len * percent):
          progress += "="
      else:
          progress += " "
#     sys.stdout.write("\r")
  sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(bar_len * percent), bar_len, percent * 100))
  sys.stdout.flush()

  return

def datetime_range(start, end, delta):
  from datetime import date, datetime, timedelta
  dt_list = []
  current = start
  if not isinstance(delta, timedelta):
      delta = timedelta(**delta)
  while current <= end:
      dt_list.append(current)
      current += delta
  return dt_list

def savefig(savedir,save_suffix,name,suffix2=''):
  import matplotlib.pyplot as plt
  if savedir:
      filename = f'{savedir}{name}{save_suffix}{suffix2}.png'
      plt.savefig(filename,facecolor='white')
      print('Figure save as ',filename)   