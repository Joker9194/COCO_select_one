"""
#-*-coding:utf-8-*-
@version: python3.8
@author: jokerwu
@contact: 1073224239@qq.com
@site: 
@software: PyCharm
@project: PycharmProjects
@file: coco_select_one.py
@time: 2022/2/8
"""
import json
import os
import shutil

from pycocotools.coco import COCO
from tqdm import tqdm

# 需要设置的路径
saveDir = r"/media/jokerwu/Backup/COCO/2017/coco/"
img_dir = saveDir + 'images/'
ann_dir = saveDir + 'annotations/'
# datasets_list = ['valminusminival2014']
datasets_list = ['train2017', 'val2017']
#
# dataDir = r"/media/jokerwu/Backup/COCO/2014/"
dataDir = r"/media/jokerwu/Backup/COCO/2017/coco_ori/"

# coco有80类，这里写要提取类的名字，以person为例
classes_names = ['person']

person_coco = dict()
person_coco['info'] = dict()
person_coco['licenses'] = []
person_coco['images'] = []
person_coco['annotations'] = []
person_coco['categories'] = []


# 添加coco info信息
def add_info(year):
    info = dict()
    if year == 2017:
        info['description'] = 'COCO 2017 Dataset'
        info['url'] = r'http://cocodataset.org'
        info['version:'] = 1.0
        info['year'] = 2017
        info['contributor'] = 'COCO Consortium'
        info['date_created'] = '2017/09/01'
    elif year == 2014:
        info['description'] = 'This is stable 1.0 version of the 2014 MS COCO dataset.'
        info['url'] = r'http://mscoco.org'
        info['version:'] = 1.0
        info['year'] = 2014
        info['contributor'] = 'Microsoft COCO group'
        info['date_created'] = '2015-01-27 09:11:52.357475'
    return info


# 添加licenses
def add_licenses():
    person_coco['licenses'] = [{"url": "http://creativecommons.org/licenses/by-nc-sa/2.0/", "id": 1,
                                "name": "Attribution-NonCommercial-ShareAlike License"},
                               {"url": "http://creativecommons.org/licenses/by-nc/2.0/", "id": 2,
                                "name": "Attribution-NonCommercial License"},
                               {"url": "http://creativecommons.org/licenses/by-nc-nd/2.0/", "id": 3,
                                "name": "Attribution-NonCommercial-NoDerivs License"},
                               {"url": "http://creativecommons.org/licenses/by/2.0/", "id": 4,
                                "name": "Attribution License"},
                               {"url": "http://creativecommons.org/licenses/by-sa/2.0/", "id": 5,
                                "name": "Attribution-ShareAlike License"},
                               {"url": "http://creativecommons.org/licenses/by-nd/2.0/", "id": 6,
                                "name": "Attribution-NoDerivs License"},
                               {"url": "http://flickr.com/commons/usage/", "id": 7,
                                "name": "No known copyright restrictions"},
                               {"url": "http://www.usa.gov/copyright.shtml", "id": 8,
                                "name": "United States Government Work"}]


# 检查目录是否存在，如果存在，先删除再创建，否则，直接创建
def mkr(path):
    if not os.path.exists(path):
        os.makedirs(path)  # 可以创建多级目录


def id2name(coco):
    classes = dict()
    for cls in coco.dataset['categories']:
        classes[cls['id']] = cls['name']
    return classes


def main(src_file, dst_file, dataset):
    dst_img_dir = os.path.join(saveDir, dataset)
    # dst_ann_dir = os.path.join(ann_dir, dataset)
    mkr(dst_img_dir)
    # mkr(dst_ann_dir)

    year = int(dataset[-4:])

    coco = COCO(src_file)
    # print(coco.info())

    person_coco['info'] = add_info(year)
    add_licenses()

    # 获取COCO数据集中的所有类别
    # classes = id2name(coco)
    # print(classes)
    # classes_ids = coco.getCatIds(catNms=classes_names)
    # print(classes_ids)
    for cls in classes_names:
        cls_id = coco.getCatIds(catNms=[cls])
        img_ids = coco.getImgIds(catIds=cls_id)
        print(cls, len(img_ids))

        for img_id in tqdm(img_ids):
            img = coco.loadImgs(img_id)[0]
            person_coco['images'].append(img)

            file_name = img['file_name']
            src_img_path = os.path.join(dataDir + '/' + dataset, file_name)
            dst_img_path = os.path.join(dst_img_dir, file_name)
            # print(src_img_path, dst_img_path)
            if dataset == 'minival2014':
                src_img_path = os.path.join(dataDir + '/val2014/', file_name)

            if dataset == 'valminusminival2014':
                pass
            else:
                shutil.copy(src_img_path, dst_img_path)

            annIds = coco.getAnnIds(imgIds=img['id'], catIds=cls_id, iscrowd=None)
            annotations = coco.loadAnns(annIds)
            for anno in annotations:
                bbox = anno['bbox']
                if bbox[2] == 0 or bbox[3] == 0:
                    print(bbox)
                    continue

                if anno['iscrowd'] == 1:
                    continue

                person_coco['annotations'].append(anno)

    person_coco['categories'].append(coco.loadCats(ids=1)[0])

    with open(dst_file, 'w') as json_file:
        json.dump(person_coco, json_file)

    # print(person_coco['categories'])


if __name__ == '__main__':
    for dataset in datasets_list:
        annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataset)
        saveAnnFile = '{}/annotations/instances_{}.json'.format(saveDir, dataset)
        main(annFile, saveAnnFile, dataset)
    print('Done')
