import sys
import argparse
import configparser
import logging
import os.path
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
# module azure permet d'accéde au cloud de l'espace de stockage 



def listb(args, containerclient):
    """cette fonction permet d'accéder au conteneur sur azure
    """
    blob_list=containerclient.list_blobs()
    for blob in blob_list:
        logging.debug("affiche le blob")
        print(blob.name)


def upload(cible, blobclient):
    """
    cette fonction permet d'envoyer le fichier sur azure 
    """
    with open(cible, "rb") as f:
        logging.warning("envoi le fichier sur le conteneur")
        blobclient.upload_blob(f)


def download(filename, dl_folder, blobclient):
    """
    cette fonction permet de telecharge le fichier depuis azure 
    """
    chemin = os.path.join(dl_folder,filename)
    with open(chemin, "wb") as my_blob:
        logging.warning("telecharge le fichier sur azure")
        blob_data=blobclient.download_blob()
        blob_data.readinto(my_blob)


def main(args,config):
    """fonction fonction principale qui permet d'accede au conteneur sur asure
    qui permet d'envoyer un fichier ou telecharger un fichier via argparse 
    """
    logging.info("debut de la fonction principale")
    blobclient=BlobServiceClient(
        f"https://{config['storage']['account']}.blob.core.windows.net",
        config["storage"]["key"],
        logging_enable=False)
        logging.debug("prend les information de config.ini qui prend les identifiant pour accede au conteneur ")
    containerclient=blobclient.get_container_client(config["storage"]["container"])
    if args.action=="list":
        logging.debug("accede au compte azure")
        return listb(args, containerclient)
    else:
        if args.action=="upload":
            logging.warning("envoi le fichier sur azure")
            blobclient=containerclient.get_blob_client(os.path.basename(args.cible))
            return upload(args.cible, blobclient)
        elif args.action=="download":
            logging.warning("telecharge le fichier sur azure")
            blobclient=containerclient.get_blob_client(os.path.basename(args.remote))
            return download(args.remote, config["general"]["restoredir"], blobclient)
    

if __name__=="__main__":
    # list des argument 
    parser=argparse.ArgumentParser("Logiciel d'archivage de documents")
    # config.ini est le fichier qui permet d'accede au conteneur grace au identifiant et clé
    parser.add_argument("-cfg",default="config.ini",help="chemin du fichier de configuration")
    parser.add_argument("-lvl",default="info",help="niveau de log")
    subparsers=parser.add_subparsers(dest="action",help="type d'operation")
    subparsers.required=True
    
    parser_s=subparsers.add_parser("upload")
    parser_s.add_argument("cible",help="fichier à envoyer")

    parser_r=subparsers.add_parser("download")
    parser_r.add_argument("remote",help="nom du fichier à télécharger")
    parser_r=subparsers.add_parser("list")

    args=parser.parse_args()

    #erreur dans logging.warning : on a la fonction au lieu de l'entier
    loglevels={"debug":logging.DEBUG, "info":logging.INFO, "warning":logging.WARNING, "error":logging.ERROR, "critical":logging.CRITICAL}
    print(loglevels[args.lvl.lower()])
    logging.basicConfig(level=loglevels[args.lvl.lower()])

    config=configparser.ConfigParser()
    config.read(args.cfg)

    sys.exit(main(args,config))