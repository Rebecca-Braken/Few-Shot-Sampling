import argparse
import random
from pathlib import Path
from datetime import datetime
from collections import Counter
from re import U

def load_data(data_path):
    data = []
    for set in ["train", "valid", "test"]:
        set_path = data_path + set + ".txt"
        with open(set_path, "r") as f:
            set_data = f.read().strip().split("\n")
            set_data = [i.split() for i in set_data]
            data += set_data
    return data


def get_entities(data):
        entities = sorted(list(set([d[0] for d in data]+[d[2] for d in data])))
        return entities

def get_relations(data):
        relations = sorted(list(set([d[1] for d in data])))
        return relations

def create_subset(dataset, min_size, max_size):
    triplets = set()
    dataset_entities = get_entities(dataset)
    #randomly select a core-entity
    entities = random.sample(dataset_entities, 1)
    new_entities = entities
    used_entities = []
    while not len(triplets) >= min_size:
        #randomly choose one of the entities of the subset
        selected_entity = random.sample(new_entities, 1)
        used_entities.append(selected_entity)
        #create set of tuples to avoid duplicate triplets 
        neighbourhood = {tuple(i) for i in dataset if i[0] in selected_entity or i[2] in selected_entity}
        merged_subgraphs = triplets.union(neighbourhood)
        if len(merged_subgraphs) > max_size:
            neighbourhood = random.sample(neighbourhood, max_size - len(triplets))
        triplets.update(neighbourhood)
        for triplet in triplets:
            entities.append(triplet[0])
            entities.append(triplet[2])
        entities = list(set(entities))
        new_entities = [ent for ent in entities if ent not in used_entities]
    subset = [i for i in triplets]
    return subset

def create_dataset_split(dataset):
    split = {"train": [], "test": [], "valid": []}
    relations = get_relations(dataset)
    for rel in relations:
        rel_triplets = [t for t in dataset if t[1] == rel]
        train = random.sample(rel_triplets, round(len(rel_triplets) * 0.85))
        rel_triplets = [t for t in rel_triplets if t not in train]
        small_split = random.sample(rel_triplets, round(len(rel_triplets) * 0.5))
        if len(small_split) < len(rel_triplets) * 0.5:
            valid = small_split
            test = [t for t in rel_triplets if t not in valid]
        else:
            test = small_split
            valid = [t for t in rel_triplets if t not in test]
        split["train"] += train
        split["test"] += test
        split["valid"] += valid
    return split


def save_data(save_path, split):
    for set in split:
        neighbourhood_data = []
        for triplet in split[set]:
            neighbourhood_data.append("\t".join([str(i) for i in triplet]))
        path = save_path + set + ".txt"
        with open(path, "w+") as f:
            f.write("\n".join(neighbourhood_data))
            f.close()


def save_dict(save_path, data):
    save_dict = {index: id for index, id in enumerate(data)}
    with open(save_path, "w+") as f:
        for key in save_dict.keys():
            f.write("%s\t%s\n" %(key, save_dict[key]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parser For Arguments',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--data', dest = 'data_set', default='WN18RR', type = str, help='Dataset to use, default: FB15k-237')
    parser.add_argument('--data_dir', dest = 'data_dir', default='./data/original/', type = str, help='Original dataset directory')
    parser.add_argument('--min_size', default = 500, type = int, help='Lower bound for dataset size')
    parser.add_argument('--max_size', default = 300000, type = int, help = 'Upper bound for dataset size')
    parser.add_argument('--save_path', dest='save_path', default = "./data/subsampled/", help='Where to save the new training set')
    
    args = parser.parse_args()
    data_path = args.data_dir + args.data_set + "/" 
    save_path = args.save_path + args.data_set + "/" + str(args.min_size) + "/" + datetime.now().strftime("%d%m%y_%H%M%S") +"/"
    Path(save_path).mkdir(parents=True, exist_ok=True)
    
    dataset = load_data(data_path)
    subset = create_subset(dataset, args.min_size, args.max_size)
    entities = list(set(get_entities(subset)))
    relations = list(set(get_relations(subset)))
    split = create_dataset_split(subset)
    save_data(save_path, split)
    entity_save_path = save_path + "/entities.dict"
    rels_save_path = save_path + "/relations.dict"
    save_dict(entity_save_path, entities)
    save_dict(rels_save_path, relations)
