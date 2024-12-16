import argparse
from riqme.sparql.EndpointRiken import Endpoint
# from riqme.sparql.Endpoint import Endpoint
from riqme.nlp.normalizer import Normalizer
# from riqme.index.whoosh_index import *
from riqme.index.import_index import *
#from riqme.index.vector_distance_index import TBoxIndex
# from riqme.index.vector_distance_index import ABoxIndex
import os
import shutil

def createIndexes(base_dir, index_t_box, endpoint_t_box_url, database):
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Base directory created: {base_dir}")

    labels_path = os.path.join(base_dir, "labels.obj")
    counts_path = os.path.join(base_dir, "counts.obj")
    index_path = os.path.join(base_dir, "t_box_index", index_t_box.lower())

    if os.path.exists(labels_path):
        os.remove(labels_path)
        print(f"Old file removed: {labels_path}")

    if os.path.exists(counts_path):
        os.remove(counts_path)
        print(f"Old file removed: {counts_path}")

    if os.path.exists(index_path):
        shutil.rmtree(index_path)
        print(f"Old index removed: {index_path}")

    print("Creating T-Box endpoint")
    endpoint_t_box = Endpoint(endpoint_t_box_url, database, labels_path, counts_path)
    print("-----------------------------------------------------------")

    print("Creating Normalizer")
    normalizer = Normalizer()
    print("-----------------------------------------------------------")

    print("Creating T-Box index")
    t_box_index = TBoxIndex(endpoint_t_box, normalizer, index_path)
    print("T-Box index created: "+str(t_box_index.exists()) + " Type: "+t_box_index.type)
    print("-----------------------------------------------------------")

    print("Saving T-Box Endpoint labels cache...")
    endpoint_t_box.save_labels()
    print("T-Box Endpoint labels Saved")

    print("Saving T-Box Endpoint counts cache...")
    endpoint_t_box.save_counts()
    print("T-Box Endpoint counts Saved")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create T-Box index.')
    parser.add_argument('--base_dir', required=True, help='Base directory for saving files')
    parser.add_argument('--index_t_box', default="FAISS", help='Index T-Box type')
    parser.add_argument('--endpoint_t_box_url', required=True, help='Endpoint T-Box URL')
    parser.add_argument('--database', required=True, help='Database name')
    args = parser.parse_args()

    createIndexes(args.base_dir, args.index_t_box, args.endpoint_t_box_url, args.database)
