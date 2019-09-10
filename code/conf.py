import os

data_dir = 'data'

source_xml = os.path.join(data_dir, 'Posts.xml')
source_csv = os.path.join(data_dir, 'Posts.csv')

train_csv = os.path.join(data_dir, 'Posts-train.csv')
test_csv = os.path.join(data_dir, 'Posts-test.csv')

train_matrix = os.path.join(data_dir, 'matrix-train.p')
test_matrix = os.path.join(data_dir, 'matrix-test.p')

model = os.path.join(data_dir, 'model.p')

