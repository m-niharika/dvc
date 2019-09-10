import hashlib
import subprocess
import time
from os import path, walk
import properties

from pandas._libs import json

file_existence = path.exists('Dvcfile')

data_Conf_file  = properties.dataConf_path
code_conf_file  = properties.codeConf_path
data_dir_path = properties.data_path
code_dir_path = properties.code_path
Key = properties.Key
SECRET_ACCESS_KEY = properties.Value

files = []
subdirs = []

def get_checksum(files,path):
    checksum_lst = []
    for file in files:
        file_path = path +'/'+file

        hasher_object = hashlib.md5()
        with open(file_path,'rb') as open_file:
            content = open_file.read()
            hasher_object.update(content)
        checksum_lst.append(hasher_object.hexdigest())
    zip_object = zip(files , checksum_lst)

    return dict(zip_object)

def update_dataConffile(dict):
    with open(data_Conf_file, 'w+') as outfile:
        json.dump(dict, outfile)

def update_codeConffile(dict):
    with open(code_conf_file, 'w+') as outfile:
        json.dump(dict, outfile)

def dir_structure(dir_path):
    for root, dirs, filenames in walk(dir_path):
        for subdir in dirs:
            subdirs.append(path.relpath(path.join(root, subdir), dir_path))

        for f in filenames:
            files.append(path.relpath(path.join(root, f), dir_path))
    return files

def gitCommands():

    git_status = 'git status -s'
    status = subprocess.call(git_status, shell=True)
    print('returned value:', status)

    git_add_code = 'git add code/'
    addcode = subprocess.call(git_add_code, shell=True)
    print('returned value:', addcode)


    git_add = 'git add .'
    add = subprocess.call(git_add, shell=True)
    print('returned value:', add)

    git_status = 'git status -s'
    status = subprocess.call(git_status, shell=True)
    print('returned value:', status)
    
    git_commit = 'git commit -m "updated" .'
    commit = subprocess.call(git_commit, shell=True)
    print('returned value:', commit)
    
    git_push = 'git push origin master'
    push = subprocess.call(git_push, shell=True)
    print('returned value:', push)


if not file_existence:
    print("Got New Code, Creating New Pipeline")
    commands = [
				'git init',
                'dvc init',
                'dvc add data/Posts.csv',
                'dvc run -d data/Posts.csv -d code/split_train_test.py -d code/conf.py -o data/Posts-test.csv -o data/Posts-train.csv python code/split_train_test.py 0.33 20180319',
                'echo "*.pyc" >> .gitignore',
                'dvc run -d code/featurization.py -d code/conf.py -d data/Posts-train.csv -d data/Posts-test.csv -o data/matrix-train.p -o data/matrix-test.p python code/featurization.py',
                'dvc run -d data/matrix-train.p -d code/train_model.py -d code/conf.py -o data/model.p  python code/train_model.py 20180319',
                'dvc run -d data/model.p -d data/matrix-test.p -d code/evaluate.py -d code/conf.py -M  data/eval.txt -f Dvcfile  python code/evaluate.py',
				'dvc remote add -d myremote s3://dvcdataaltran/sourcedata/',
				'setx AWS_ACCESS_KEY_ID Key',
				'setx AWS_SECRET_ACCESS_KEY SECRET_ACCESS_KEY',
                'dvc pipeline show --ascii',
				'dvc push'
                ]
    p = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for cmd in commands:
        p.stdin.write(cmd + "\n")
    p.stdin.close()
    print(p.stdout.read())

    git_remote = 'git remote add origin https://github.com/m-niharika/dvc.git'
    remote = subprocess.call(git_remote, shell=True)

    gitCommands()
    data_files = dir_structure(data_dir_path)
    data_dict = get_checksum(data_files,data_dir_path)
    update_dataConffile(data_dict)
    files=[]
    
    code_files = dir_structure(code_dir_path)
    code_dict = get_checksum(code_files, code_dir_path)
    update_codeConffile(code_dict)

else:
    print("Looking for updated files")
    updated_data_files = dir_structure(data_dir_path)
    updated_data_dict = get_checksum(updated_data_files, data_dir_path)
    files = []

    with open(data_Conf_file, 'rb') as json_file:
        last_data_info = json.load(json_file)

    for key in updated_data_dict:
        if key in last_data_info:
            if(updated_data_dict[key]!=last_data_info[key]):
                print("updated----",key,updated_data_dict[key])
                print("last-----",key,last_data_info[key])

                commands = ['dvc add data\Posts.csv',
                            'dvc push']
                p = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                for cmd in commands:
                    p.stdin.write(cmd + "\n")
                p.stdin.close()
                print(p.stdout.read())
                gitCommands()
    update_dataConffile(updated_data_dict)

    updated_code_files = dir_structure(code_dir_path)
    updated_code_dict = get_checksum(updated_code_files, code_dir_path)

    with open(code_conf_file, 'rb') as json_file:
        last_code_info = json.load(json_file)

    for key in updated_code_dict:
        if key in last_code_info:
            if(updated_code_dict[key]!=last_code_info[key]):
                print("updated----",key,updated_code_dict[key])
                print("last-----",key,last_code_info[key])
                gitCommands()

    update_codeConffile(updated_code_dict)























