import glob
list_of_files = []
for file in glob.glob('data/*.out'):
    list_of_files.append(file)
print('\n'.join(list_of_files))