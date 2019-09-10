import shutil
import os

if __name__ == '__main__':
    print('Setting up/resetting')
    with open('./firstrun', 'w') as fr_file:
        fr_file.writelines(['1\n'])
    with open('./datastore.txt', 'w') as datastore:
        datastore.writelines(['0\n', '0\n'])
        try:
            shutil.rmtree('./tovisit/')
            shutil.rmtree('./visited/')
        except: pass
        os.mkdir('./tovisit/')
        os.mkdir('./visited/')
    print('Done')